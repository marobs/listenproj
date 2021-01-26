from unittest import mock, TestCase
from unittest.mock import patch, Mock, MagicMock

from werkzeug.security import generate_password_hash

from dao import login_dao_in_memory as login_dao
from service import reddit_service
from service.reddit_service import RedditException


class Test(TestCase):

    """
    works:
    Artist - Title
    Artist --- Title

    don't work:
    - Artist - Title
    Artist Title -
    Artist Title
    --
    -

    work but erm...
    Artist - - Title
    Art-ist -- Title
    """
    def test_get_song_from_post_ok(self):
        self.assertEqual(('Artist', 'Song'), reddit_service.get_song_from_post('Artist - Song'))
        self.assertEqual(('Artist', 'Song'), reddit_service.get_song_from_post('Artist -- Song'))
        self.assertEqual(('Artist', 'Song'), reddit_service.get_song_from_post('Artist --- Song'))

    def test_get_song_from_post_malformed(self):
        self.assertEqual(('Art', 'ist'), reddit_service.get_song_from_post('Art-ist - Song'))

    def test_get_song_from_post_dash_before_artist(self):
        with self.assertRaises(RedditException):
            reddit_service.get_song_from_post('- Artist - Song')

    def test_get_song_from_post_no_dash(self):
        with self.assertRaises(RedditException):
            reddit_service.get_song_from_post('Artist Song')

    def test_get_song_from_post_dash_at_end(self):
        with self.assertRaises(RedditException):
            reddit_service.get_song_from_post('Artist Song -')

    def test_get_song_from_post_only_dash(self):
        with self.assertRaises(RedditException):
            reddit_service.get_song_from_post('-')
        with self.assertRaises(RedditException):
            reddit_service.get_song_from_post('--')
