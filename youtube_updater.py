import requests
import json
import sys
import redis

from telethon.sync import TelegramClient
from telethon import functions

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
client = TelegramClient('{}/anon.session'.format(WORK_DIR), api_id, api_hash)
client.connect()
channel = client.get_entity(channel_share_link)


def is_saved(__video_id__):
    conn = redis.Redis(connection_pool=pool)
    return conn.hexists(REDIS_KEY_NAME, __video_id__)


def push_to_redis(__video_id__, __title__):
    conn = redis.Redis(connection_pool=pool)
    conn.hset(REDIS_KEY_NAME, __video_id__, __title__)


def get_latest_videos_from_channel(__channel_id__):
    url = "{}/search?part=snippet&channelId={}&order=date&type=video&maxResults=50&key={}".format(
        BASE, __channel_id__, APP_KEY)
    latest_videos = json.loads(requests.get(url).text)
    if len(latest_videos["items"]) > 0:
        ids_list = ""
        for item in latest_videos["items"]:
            ids_list += item["id"]["videoId"] + ","
        ids_list = ids_list[:-1]
        video_detail_url = "{}/videos?id={}&part=contentDetails&key={}".format(BASE, ids_list, APP_KEY)
        video_details = json.loads(requests.get(video_detail_url).text)
        for i in range(len(video_details["items"])):
            duration = video_details["items"][i]["contentDetails"]["duration"]
            if 'S' not in duration:
                duration += '0S'
            if 'M' not in duration and 'H' in duration:
                duration = duration[:duration.find('H') + 1] + '0M' + duration[duration.find('H') + 1:]
            duration = duration.replace("H", ":").replace("M", ":").replace("S", "").replace("PT", "")
            duration = ":".join([elem if len(elem) == 2 else "0" + elem for elem in duration.split(":")])
            latest_videos["items"][i]["duration"] = duration
        return latest_videos["items"]


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
        for item in channel_latest_videos:
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            video_url = "https://www.youtube.com/watch?v={}".format(video_id)
            duration = item["duration"]
            time_published = item["snippet"]["publishedAt"]
            if not is_saved(video_id):
                client(functions.messages.SendMessageRequest(
                    peer=channel,
                    message='{}\n\n{}\n\n{}'.format(title, time_published, video_url),
                    no_webpage=False
                ))
                push_to_redis(video_id, title)


if __name__ == "__main__":
    main()
