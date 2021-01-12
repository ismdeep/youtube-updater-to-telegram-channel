import requests
import json
import sys
import redis

from telethon.sync import TelegramClient
from telethon.sync import functions

WORK_DIR = sys.argv[1]
BASE = "https://www.googleapis.com/youtube/v3"
APP_KEY = open("{}/youtube_app_key.txt".format(WORK_DIR), "r").readline().strip()
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
channel = client.get_entity(channel_share_link)


class VideoInfo(object):
    video_id = None
    video_title = None
    publish_time = None
    channel_title = None

    def __init__(self, __video_id__, __video_title__, __channel_title__, __publish_time__):
        self.video_id = __video_id__
        self.video_title = __video_title__
        self.channel_title = __channel_title__
        self.publish_time = __publish_time__

    def __str__(self):
        return "[{}, {}, {}]".format(self.video_id, self.video_title, self.publish_time)


def is_saved(__video_id__):
    conn = redis.Redis(connection_pool=pool)
    return conn.hexists(REDIS_KEY_NAME, __video_id__)


def push_to_redis(__video_id__, __title__):
    conn = redis.Redis(connection_pool=pool)
    conn.hset(REDIS_KEY_NAME, __video_id__, __title__)


def get_latest_videos_from_channel(__channel_id__):
    url = "{}/search?part=snippet" \
          "&channelId={}" \
          "&order=date" \
          "&type=video" \
          "&maxResults=25" \
          "&key={}".format(BASE, __channel_id__, APP_KEY)
    latest_videos = json.loads(requests.get(url).text)
    if 'error' in latest_videos:
        print(latest_videos['error'])
        exit(0)
        return []
    if 'items' not in latest_videos:
        return []
    videos = []
    for item in latest_videos["items"]:
        videos.append(VideoInfo(
            item["id"]["videoId"],
            item['snippet']['title'],
            item['snippet']['channelTitle'],
            item['snippet']['publishedAt']
        ))
    return videos


def main():
    channel_list_file_path = "{}/news_list.txt".format(WORK_DIR)
    channels_list = []
    with open(channel_list_file_path) as f:
        for line in f:
            channel_id = line.split()[0].strip()
            if len(channel_id) > 0:
                channels_list.append(channel_id)
    for channel_id in channels_list:
        channel_latest_videos = get_latest_videos_from_channel(channel_id)
        for video in channel_latest_videos[::-1]:
            video_url = "https://www.youtube.com/watch?v={}".format(video.video_id)
            if not is_saved(video.video_id):
                client(functions.messages.SendMessageRequest(
                    peer=channel,
                    message='【{}】 {}\n\n{}\n\n{}'.format(
                        video.channel_title,
                        video.video_title,
                        video.publish_time,
                        video_url
                    ),
                    no_webpage=False
                ))
                push_to_redis(video.video_id, video.video_title)


if __name__ == "__main__":
    main()
