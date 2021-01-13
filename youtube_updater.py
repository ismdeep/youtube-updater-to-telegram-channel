import requests
import json
import sys
import redis
import time

from telethon.sync import TelegramClient
from telethon.sync import functions

WORK_DIR = sys.argv[1]
REDIS_KEY_NAME = 'youtube_videos'

# 1. Get Redis Configuration
redis_config = json.load(open(WORK_DIR + '/redis.json', 'r'))
pool = redis.ConnectionPool(host=redis_config['host'], port=redis_config['port'])
try:
    redis.Redis(connection_pool=pool).ping()
except Exception as e:
    print(e)
    exit(-1)

# 2. Config Telegram Bot
telegram_bot_config = json.load(open(WORK_DIR + '/telegram_bot.json', 'r'))
api_id = telegram_bot_config['api_id']
api_hash = telegram_bot_config['api_hash']
channel_share_link = telegram_bot_config['channel_share_link']
client = TelegramClient(WORK_DIR + '/anon.session', api_id, api_hash)
client.connect()
telegram_channel = client.get_entity(channel_share_link)


class ChannelInfo(object):
    channel_id = None
    channel_title = None

    def __init__(self, __channel_id__, __channel_title__):
        self.channel_id = __channel_id__
        self.channel_title = __channel_title__

    def __str__(self):
        return "[{}, {}]".format(self.channel_id, self.channel_title)


class VideoInfo(object):
    video_id = None
    video_title = None
    publish_time = None

    def __init__(self):
        pass

    def set_video_id(self, __video_id__):
        self.video_id = __video_id__
        return self

    def set_video_title(self, __video_title__):
        self.video_title = __video_title__
        return self

    def set_publish_time(self, __publish_time__):
        self.publish_time = __publish_time__
        return self

    def __str__(self):
        return "[{}, {}, {}]".format(self.video_id, self.video_title, self.publish_time)


def is_saved(__video_id__):
    conn = redis.Redis(connection_pool=pool)
    return conn.hexists(REDIS_KEY_NAME, __video_id__)


def push_to_redis(__video_id__, __title__):
    conn = redis.Redis(connection_pool=pool)
    conn.hset(REDIS_KEY_NAME, __video_id__, __title__)


def get_video_info(__video_id__) -> VideoInfo:
    video_url = "https://www.youtube.com/watch?v={}".format(__video_id__)
    content = requests.get(url=video_url).text
    publish_time = content[content.find('''"publishDate":"''') + len('''"publishDate":"'''):]
    publish_time = publish_time[:publish_time.find('''"''')]
    title = content[content.find('''"><title>''') + len('''"><title>'''):]
    title = title[:title.find(" - YouTube</title>")]
    return VideoInfo().set_video_id(__video_id__).set_publish_time(publish_time).set_video_title(title)


def get_latest_videos_from_channel(__channel_id__) -> [VideoInfo]:
    req = requests.get(url="https://www.youtube.com/channel/{}".format(__channel_id__))
    content = req.text
    content = content[content.find('''{"horizontalListRenderer":{"items":'''):]
    videos = []
    while content.find('''{"videoIds":["''') >= 0:
        content = content[content.find('''{"videoIds":["''') + len('''{"videoIds":["'''):]
        video_id = content[:content.find('''"''')]
        videos.append(get_video_info(video_id))
    return videos


def load_channels():
    channel_list_file_path = "{}/news_list.txt".format(WORK_DIR)
    channel_list = []
    with open(channel_list_file_path) as f:
        for line in f:
            channel_id = line.split()[0].strip()
            if len(channel_id) > 0:
                channel_list.append(ChannelInfo(
                    channel_id,
                    line[len(channel_id):].strip()
                ))
    return channel_list


def watch_channel(__channel__: ChannelInfo):
    channel_latest_videos = get_latest_videos_from_channel(__channel__.channel_id)
    print(time.asctime(), __channel__.channel_id, __channel__.channel_title, len(channel_latest_videos))
    for video in channel_latest_videos:
        video_url = "https://www.youtube.com/watch?v={}".format(video.video_id)
        if not is_saved(video.video_id):
            client(functions.messages.SendMessageRequest(
                peer=telegram_channel,
                message='【{}】[{}] {}\n\n{}'.format(
                    __channel__.channel_title,
                    video.publish_time,
                    video.video_title,
                    video_url
                ),
                no_webpage=False
            ))
            push_to_redis(video.video_id, __channel__.channel_id)


def main():
    channels = load_channels()
    [watch_channel(channel) for channel in channels]


if __name__ == "__main__":
    main()
