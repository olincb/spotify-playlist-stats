import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import choice

class Playlistats:


    def __init__(self) -> None:
        self.auth_manager = SpotifyClientCredentials()
        self.sp_api = spotipy.Spotify(auth_manager=self.auth_manager)


    def example_playlist_id(self, category_id='featured'):
        if category_id == 'featured':
            pls = self.sp_api.featured_playlists(limit=50)['playlists']['items']
        else:
            pls = self.sp_api.category_playlists(category_id, limit=50)['playlists']['items']
        ex_pl = choice(pls)
        return ex_pl['id']


    def playlist_id_search(self, query):
        '''
        feeling lucky?
        returns the id of the first playlist returned by a search
        '''
        return self.sp_api.search(query, limit=1, type='playlist')['playlists']['items'][0]['id']


    def basic_info(self, id, fields=None, market=None, additional_types=('track', )):
        return self.sp_api.playlist(id, fields=fields, market=market, additional_types=additional_types)


    def all_tracks(self, id):
        resp = self.sp_api.playlist_items(id)
        tracks = resp['items']
        while resp['next']:
            resp = self.sp_api.next(resp)
            tracks += resp['items']
        return tracks


    def track_count(self, id):
        return len(self.all_tracks(id))


if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    print("playlistats!")
    plsts = Playlistats()
    # pp.pprint(plsts.sp_api.featured_playlists(limit=50))
    # ex_id = plsts.example_playlist_id()
    ex_id = "https://open.spotify.com/playlist/4AfSnWDVWMeA6NeNjJjYsS?si=558f789c4c0c463c"
    # tracks = plsts.all_tracks(ex_id)
    pp.pprint(plsts.playlist_id_search("Backyard BBQ"))

