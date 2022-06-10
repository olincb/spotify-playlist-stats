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
