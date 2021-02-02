import json
import sys
import time

from telethon.sync import TelegramClient
from telethon.sync import functions

from utils.youtube_utils import ChannelInfo, get_video_info, get_latest_video_ids_from_channel
from utils.sqlite_util import EasySqlite
from utils.config_utils import load_channels
from utils.youtube_utils import download_mp3, remove_local_mp3

WORK_DIR = sys.argv[1]
REDIS_KEY_NAME = 'youtube_videos'

save_only_flag = False

create_table_sql = '''create table t_videos (
id INTEGER primary key AUTOINCREMENT not null,
video_id text not null);'''

db = EasySqlite("{}/data.db".format(WORK_DIR))
try:
    db.execute("select count(id) from t_videos", result_dict=True)
except:
    db.execute(create_table_sql)

# 2. Config Telegram Bot
telegram_bot_config = json.load(open(WORK_DIR + '/telegram_bot.json', 'r'))
api_id = telegram_bot_config['api_id']
api_hash = telegram_bot_config['api_hash']
channel_share_link = telegram_bot_config['channel_share_link']
client = TelegramClient(WORK_DIR + '/anon.session', api_id, api_hash)
client.connect()
telegram_channel = client.get_entity(channel_share_link)

channel_list_file_path = "{}/news_list.txt".format(WORK_DIR)


def is_saved(__video_id__):
    result = db.execute("select count(id) as cnt from t_videos where video_id = '{}'".format(__video_id__))[0]['cnt']
    result = int(result)
    return True if result > 0 else False


def push_to_db(__video_id__, __title__):
    print("Push {} to db".format(__video_id__))
    db.insert("insert into t_videos (video_id) values('{}')".format(__video_id__))


def watch_channel(__channel__: ChannelInfo):
    channel_latest_video_ids = get_latest_video_ids_from_channel(__channel__.channel_id)
    print(time.asctime(), __channel__.channel_id, __channel__.channel_title, len(channel_latest_video_ids))
    for video_id in channel_latest_video_ids:
        if not is_saved(video_id):
            video_info = get_video_info(video_id)
            # 跳过预播视频
            if video_info.is_at_premiere:
                continue
            if video_info.publish_time >= '2021-01-01':
                client(functions.messages.SendMessageRequest(
                    peer=telegram_channel,
                    message='【{}】[{}] {}\n\n{}\n\n'.format(
                        __channel__.channel_title,
                        video_info.publish_time,
                        video_info.video_title,
                        "https://www.youtube.com/watch?v={}".format(video_id)
                    ),
                    no_webpage=False
                ))
                try:
                    download_mp3(video_id)
                    client.send_file(telegram_channel, "{}.mp3".format(video_id), caption=video_info.video_title)
                    remove_local_mp3(video_id)
                except:
                    pass
            push_to_db(video_id, __channel__.channel_id)


def load_save_only_flag():
    global save_only_flag
    for item in sys.argv:
        if item == '--save-only':
            save_only_flag = True


def main():
    load_save_only_flag()
    channels = load_channels(channel_list_file_path)
    [watch_channel(channel) for channel in channels]


if __name__ == "__main__":
    main()
