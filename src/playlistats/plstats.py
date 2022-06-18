import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import choice
from collections import Counter
import requests
import re
from bs4 import BeautifulSoup
import urllib
import math

class Playlistats:


    _TRANSFORM_EXPONENT_BASE = 1.43
    _AMPLIFY_MULTIPLIER = 22
    _AMPLIFY_SHIFT = 0.5


    def __init__(self) -> None:
        self.auth_manager = SpotifyClientCredentials()
        self.sp_api = spotipy.Spotify(auth_manager=self.auth_manager)


    def example_playlist_id(self, category_id: str = 'featured') -> str:
        if category_id == 'featured':
            pls = self.sp_api.featured_playlists(limit=50)['playlists']['items']
        else:
            pls = self.sp_api.category_playlists(category_id, limit=50)['playlists']['items']
        ex_pl = choice(pls)
        return ex_pl['id']


    def playlist_id_search(self, query: str) -> str:
        '''
        feeling lucky?
        returns the id of the first playlist returned by a search
        '''
        return self.sp_api.search(query, limit=1, type='playlist')['playlists']['items'][0]['id']


    def basic_info(self, id: str, **kwargs) -> dict:
        ''' kwargs: fields, market, additional_types '''
        return self.sp_api.playlist(id, **kwargs)


    def all_tracks(self, id: str) -> list:
        resp = self.sp_api.playlist_items(id, additional_types=('track',))
        tracks = resp['items']
        while resp['next']:
            resp = self.sp_api.next(resp)
            tracks += resp['items']
        return tracks


    def track_count(self, id: str = None, tracks: list = None) -> int:
        tracks = self._tracks_from_id_or_tracks(id, tracks)
        return len(tracks)

    
    def _tracks_from_id_or_tracks(self, id, tracks):
        if id == None and tracks == None:
            raise ValueError("Need one of id or tracks.")
        elif id and tracks:
            print("Warning: id and tracks passed; using tracks.")

        if tracks == None:
            tracks = self.all_tracks(id)
        return tracks

    def artists(self, id: str = None, tracks: list = None) -> list:
        tracks = self._tracks_from_id_or_tracks(id, tracks)

        # first get all artists and their genres at one time
        # so we don't have to keep querying spotify
        artist_ids = set()

        for track in tracks:
            if not track['is_local']:
                for artist in track['track']['artists']:
                    artist_ids.add(artist['id'])
        artist_ids = list(artist_ids)

        # get genre information for each artist
        request_list = []
        artists_info = []

        # spotify api can only handle 50 artists at a time
        while artist_ids:
            request_list.append(artist_ids[:50])
            artist_ids = artist_ids[50:]

        # make the requests and concatenate the results
        for ids in request_list:
            artists = self.sp_api.artists(ids)['artists']
            artists_info = artists_info + artists
        
        return artists_info

    
    def _artists_from_id_tracks_or_artists(self, id, tracks, artists):
        if id == None and tracks == None and artists == None:
            raise ValueError("Need one of id, tracks, or artists.")
        elif (id or tracks) and artists:
            print("Warning: id or tracks passed in addition to artists; using artists.")

        if artists == None:
            artists = self.artists(id=id, tracks=tracks)
        return artists

    
    def artist_genres(self, id: str = None, tracks: list = None, artists: list = None) -> dict:
        artists = self._artists_from_id_tracks_or_artists(id, tracks, artists)
        return {artist_info['id']: artist_info['genres'] for artist_info in artists}

    
    def artist_ids(self, id: str = None, tracks: list = None, artists: list = None) -> list:
        artists = self._artists_from_id_tracks_or_artists(id, tracks, artists)
        return [artist_info['id'] for artist_info in artists]


    def artist_counts(self, id: str = None, tracks: list = None) -> Counter:
        tracks = self._tracks_from_id_or_tracks(id, tracks)

        artist_count = Counter()
        for track in tracks:
            if not track['is_local']:
                for artist in track['track']['artists']:
                    artist_count[artist['id']] += 1
        return artist_count


    def genre_counts(self, id: str = None, tracks: list = None) -> Counter:
        tracks = self._tracks_from_id_or_tracks(id, tracks)

        # get genre information for each artist
        artist_genres = self.artist_genres(tracks=tracks)

        # loop through tracks again now that we have the artists' genre information
        # we only want one of each genre per track, but then we'll increment the total genre count
        all_genres = Counter()
        for track in tracks:
            track_genres = set()
            if not track['is_local']:
                for artist in track['track']['artists']:
                    track_genres.update(artist_genres[artist['id']])
            for genre in track_genres:
                all_genres[genre] += 1
        
        # sort the counter before returning it
        return Counter({k:v for k, v in all_genres.most_common()})

    
    def most_common_genres(self, id: str = None, n: int = 10, tracks: list = None) -> list:
        genre_counts = self.genre_counts(id, tracks)
        return [k for k, _ in genre_counts.most_common(n)]


    def most_common_genres_with_ratios(self, id: str = None, n: int = 10, tracks: list = None) -> dict:
        tracks = self._tracks_from_id_or_tracks(id, tracks)
        genre_counts = self.genre_counts(tracks=tracks)
        num_tracks = self.track_count(tracks=tracks)
        return {k: v/num_tracks for k, v in genre_counts.most_common(n)}

    
    def _genre_cts_from_id_tracks_or_genre_cts(self, id, tracks, genre_cts):
        if id == None and tracks == None and genre_cts == None:
            raise ValueError("Need one of id, tracks, or genre_cts.")
        elif (id or tracks) and genre_cts:
            print("Warning: id or tracks passed in addition to genre_cts; using genre_cts.")

        if genre_cts == None:
            genre_cts = self.genre_counts(id=id, tracks=tracks)
        return genre_cts
    

    def num_genres(self, id: str = None, tracks: list = None, genre_cts: Counter = None) -> int:
        genre_cts = self._genre_cts_from_id_tracks_or_genre_cts(id, tracks, genre_cts)
        return len(genre_cts)


    def _get_acoustic_dists(self, genre_counts):
        genre_dists = {}
        important_genres = genre_counts.keys()
        
        dist_getter = re.compile(r'.*acoustic distance: (\d+\.\d+)')
        rootgenre = genre_counts.most_common(1)[0][0]
        # make the request
        url = 'https://everynoise.com/everynoise1d.cgi?root={}&scope=all'.format(urllib.parse.quote(rootgenre))
        r = requests.get(url)
        # troubleshooting faulty requests
        while not r.ok:
            print(r)
            r = requests.get(url) # maybe another try will help
            
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # get all rows
        rows = soup.find("table").find_all("tr")
        # in each row, find the name of the target genre, and the acoustic distance
        for row in rows:
            cells = row.find_all("td")
            targetgenre = cells[2].find('a').get_text()
            if targetgenre in important_genres:
                distelem = cells[0]
                if not distelem.has_attr('title'):
                    print(str(distelem) + ' ' + rootgenre + ' ' + targetgenre)
                else: 
                    title = distelem['title']
                    dist = float(dist_getter.search(title).group(1))
                    genre_dists[targetgenre] = dist
        return genre_dists


    def _get_acoustic_dist_weighted_avg(self, genre_counts):
        dists = self._get_acoustic_dists(genre_counts)
        running_sum = 0
        for genre in genre_counts.keys():
            running_sum += genre_counts[genre] * dists[genre]
        return running_sum / sum(genre_counts.values())


    def score_cohesiveness(self, id: str = None, tracks: list = None, genre_cts: Counter = None) -> float:
        genre_cts = self._genre_cts_from_id_tracks_or_genre_cts(id, tracks, genre_cts)
        adwa = self._get_acoustic_dist_weighted_avg(genre_cts)
        score = self._transform_posR_to_zero_to_one(adwa)
        amplified_score = self._amplify(score)
        return amplified_score


    def _transform_posR_to_zero_to_one(self, adwa):
        return 1/(self._TRANSFORM_EXPONENT_BASE**adwa)


    def _amplify(self, x):
        return 1/(1+math.exp(-self._AMPLIFY_MULTIPLIER * (x - self._AMPLIFY_SHIFT)))

    
    def _calibrate_scoring_constants(self, acoustic_dist_wavg: float, transform_exp_base: float, amp_mult: float, amp_shift: float = 0.5):
        def calibration_transform_posR_to_zero_to_one(adwa):
            return 1/(transform_exp_base**adwa)

        def calibration_amplify(x):
            return 1/(1+math.exp(-amp_mult * (x - amp_shift)))
        
        score = calibration_transform_posR_to_zero_to_one(acoustic_dist_wavg)
        amplified_score = calibration_amplify(score)
        return amplified_score


    def genre_track_ratio(self, id: str = None, tracks: list = None) -> float:
        tracks = self._tracks_from_id_or_tracks(id, tracks)
        nt = self.track_count(tracks=tracks)
        ng = self.num_genres(tracks=tracks)
        return ng/nt


    def track_genre_ratio(self, id: str = None, tracks: list = None) -> float:
        tracks = self._tracks_from_id_or_tracks(id, tracks)
        nt = self.track_count(tracks=tracks)
        ng = self.num_genres(tracks=tracks)
        return nt/ng


if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    print("playlistats!")
    plsts = Playlistats()
    # pp.pprint(plsts.sp_api.featured_playlists(limit=50))
    # ex_id = plsts.example_playlist_id()
    ex_id = "https://open.spotify.com/playlist/3qygNROI3qOZJkYp2F4opi?si=ef8dc596ca824139"
    tracks = plsts.all_tracks(ex_id)
    artists = plsts.artists(id=ex_id)
    print(artists)

