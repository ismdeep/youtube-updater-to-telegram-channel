from utils.telegram_utils import Telegram


import unittest
import os.path

from utils.youtube_utils import download_mp3, remove_local_mp3, get_video_info, get_latest_video_ids_from_channel


class TestTelegramUtils(unittest.TestCase):
    def test_send_msg(self):
        telegram = Telegram()
        telegram.load_config('/Users/ismdeep/Projects/youtube-updater-to-telegram-channel/data/telegram_bot.json')
        telegram.send_msg("Hi")

    def test_send_mp3_file(self):
        telegram = Telegram()
        telegram.load_config('/Users/ismdeep/Projects/youtube-updater-to-telegram-channel/data/telegram_bot.json')
        telegram.send_mp3_file("/Users/ismdeep/Projects/youtube-updater-to-telegram-channel/data/ZuFQykdZAWE.mp3",
                               "Hello")


if __name__ == '__main__':
    unittest.main()
