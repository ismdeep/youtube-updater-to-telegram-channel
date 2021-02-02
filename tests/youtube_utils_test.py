import unittest
import os.path

from utils.youtube_utils import download_mp3, remove_local_mp3, get_video_info, get_latest_video_ids_from_channel


class TestDownloadMethod(unittest.TestCase):
    def test_download_mp3(self):
        video_id = "eK7lZJLdBfQ"
        remove_local_mp3(video_id)
        download_mp3('/usr/local/bin/youtube-dl', video_id)
        self.assertTrue(os.path.exists("{}.mp3".format(video_id)))
        remove_local_mp3(video_id)

    def test_remove_local_mp3(self):
        video_id = "eK7lZJLdBfQ"
        remove_local_mp3(video_id)
        download_mp3('/usr/local/bin/youtube-dl', video_id)
        self.assertTrue(os.path.exists("{}.mp3".format(video_id)))
        remove_local_mp3(video_id)
        self.assertFalse(os.path.exists("{}.mp3".format(video_id)))

    def test_get_video_info(self):
        video_id = "eK7lZJLdBfQ"
        video_info = get_video_info(video_id)
        print(video_info.video_title)
        print(video_info.publish_time)
        print(video_info.is_at_premiere)

    def test_get_latest_video_ids_from_channel(self):
        video_ids = get_latest_video_ids_from_channel('UCMUnInmOkrWN4gof9KlhNmQ')
        print(video_ids)


if __name__ == '__main__':
    unittest.main()
