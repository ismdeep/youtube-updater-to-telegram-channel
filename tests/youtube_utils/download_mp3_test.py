import unittest
import os.path

from utils.youtube_utils import download_mp3, remove_local_mp3


class TestDownloadMethod(unittest.TestCase):
    def test_download_mp3(self):
        video_id = "Lt4Z5oOAeEY"
        remove_local_mp3(video_id)
        download_mp3(video_id)
        self.assertTrue(os.path.exists("{}.mp3".format(video_id)))
        remove_local_mp3(video_id)

    def test_remove_local_mp3(self):
        video_id = "Lt4Z5oOAeEY"
        remove_local_mp3(video_id)
        download_mp3(video_id)
        self.assertTrue(os.path.exists("{}.mp3".format(video_id)))
        remove_local_mp3(video_id)
        self.assertFalse(os.path.exists("{}.mp3".format(video_id)))


if __name__ == '__main__':
    unittest.main()
