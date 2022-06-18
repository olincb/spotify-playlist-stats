import sys
sys.path.append('./src')
sys.path.append('../src')

import unittest
from playlistats.plstats import Playlistats
from spotipy.exceptions import SpotifyException

class TestPlaylistats(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.plsts = Playlistats()


    def setUp(self):
        self.test_id = TestPlaylistats.plsts.example_playlist_id()


    def test_example_playlist_id(self):
        ex_id = TestPlaylistats.plsts.example_playlist_id(category_id='jazz')
        ex_id2 = TestPlaylistats.plsts.example_playlist_id()
        _ = TestPlaylistats.plsts.basic_info(ex_id)
        _ = TestPlaylistats.plsts.basic_info(ex_id2)


    def test_playlist_id_search(self):
        ex_id = TestPlaylistats.plsts.playlist_id_search('Backyard BBQ')
        _ = TestPlaylistats.plsts.basic_info(ex_id)


    def test_invalid_id(self):
        with self.assertRaises(SpotifyException):
            _ = TestPlaylistats.plsts.basic_info("not an id")


    def test_basic_info(self):
        r = TestPlaylistats.plsts.basic_info(self.test_id)
        self.assertEqual(r['type'], 'playlist')
        self.assertEqual(r['id'], self.test_id)


    def test_all_tracks(self):
        r = TestPlaylistats.plsts.all_tracks(self.test_id)
        self.assertTrue(len(r) > 0)
        self.assertEqual(type(r), list)


    def test_track_count(self):
        ts = TestPlaylistats.plsts.all_tracks(self.test_id)
        l = TestPlaylistats.plsts.track_count(self.test_id)
        self.assertEqual(len(ts), l)


    def test_artists(self):
        # TODO
        pass


    def test_artist_genres(self):
        # TODO
        pass


    def test_artist_ids(self):
        # TODO
        pass


    def test_artist_counts(self):
        # TODO
        pass


    def test_genre_counts(self):
        # TODO
        pass

    
    def test_most_common_genres(self):
        TSo_Dream_Pop_id = '2A5zN7OTP4n64gEtsFEO2Z'
        TSo_Chamber_Psych_id = '6rirvdbul7rDunT5SP5F4m'
        dream_pop_most_common = TestPlaylistats.plsts.most_common_genres(TSo_Dream_Pop_id)
        chamber_psych_most_common = TestPlaylistats.plsts.most_common_genres(TSo_Chamber_Psych_id, n=7)

        self.assertEqual(dream_pop_most_common[0], 'dream pop')
        self.assertEqual(chamber_psych_most_common[0], 'chamber psych')
        self.assertEqual(len(chamber_psych_most_common), 7)


    def test_most_common_genres_with_ratios(self):
        TSoE_link = 'https://open.spotify.com/playlist/69fEt9DN5r4JQATi52sRtq?si=42d7a1d3592f45c7'
        TSo_Dream_Pop_id = '2A5zN7OTP4n64gEtsFEO2Z'
        TSo_Chamber_Psych_id = '6rirvdbul7rDunT5SP5F4m'
        TSo_New_Rave_link = 'https://open.spotify.com/playlist/3ZlEqn2WSADG2wVMPhKHsd?si=0f82acff541743f7'
        everything_most_common = TestPlaylistats.plsts.most_common_genres_with_ratios(TSoE_link, n=1)
        dream_pop_most_common = TestPlaylistats.plsts.most_common_genres_with_ratios(TSo_Dream_Pop_id, n=1)
        chamber_psych_most_common = TestPlaylistats.plsts.most_common_genres_with_ratios(TSo_Chamber_Psych_id, n=1)
        new_rave_most_common = TestPlaylistats.plsts.most_common_genres_with_ratios(TSo_New_Rave_link, n=1)

        genre_specific_top_ratios = [list(d.values())[0] for d in [dream_pop_most_common, chamber_psych_most_common, new_rave_most_common]]
        above_95_pct = [r > 0.95 for r in genre_specific_top_ratios]

        self.assertTrue(all(above_95_pct))
        self.assertTrue(list(everything_most_common.values())[0] < 0.05)


    def test_score_cohesiveness(self):
        score = TestPlaylistats.plsts.score_cohesiveness(self.test_id)
        self.assertEqual(type(score), float)
        self.assertGreater(score, 0)
        self.assertLess(score, 1)

    
    def test_genre_track_ratio(self):
        # TODO
        pass


    def test_track_genre_ratio(self):
        # TODO
        pass


if __name__ == '__main__':
    unittest.main()
