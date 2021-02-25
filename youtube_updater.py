import sys
import time
import json
import codecs

from utils.youtube_utils import ChannelInfo, get_latest_videos
from utils.sqlite_util import EasySqlite
from utils.config_utils import load_channels
from utils.telegram_utils import Telegram
from utils.process_utils import is_other_running

if is_other_running():
    print('Other process is running. Exit...')
    exit(0)

content = codecs.open(sys.argv[1], 'r').read()
config = json.loads(content)

create_table_sql = '''create table t_videos (
id INTEGER primary key AUTOINCREMENT not null,
video_id text not null);'''

db = EasySqlite(config['db'])
try:
    db.execute("select count(id) from t_videos", result_dict=True)
except:
    db.execute(create_table_sql)

# 2. Config Telegram Bot
telegram = Telegram()
telegram.load_config(config['telegram_config'])

channel_list_file_path = config['channel']


def is_saved(__video_id__):
    result = db.execute("select count(id) as cnt from t_videos where video_id = '{}'".format(__video_id__))[0]['cnt']
    result = int(result)
    return True if result > 0 else False


def push_to_db(__video_id__, __title__):
    print("Push {} to db".format(__video_id__))
    db.insert("insert into t_videos (video_id) values('{}')".format(__video_id__))


def watch_channel(__channel__: ChannelInfo):
    videos = get_latest_videos(__channel__.channel_id)
    print(time.asctime(), __channel__.channel_id, __channel__.channel_title, len(videos))
    print(videos)
    for video in videos:
        if not is_saved(video['id']):
            caption = '【{}】{}'.format(__channel__.channel_title,
                                      video['title'])
            video_url = "https://www.youtube.com/watch?v={}".format(video['id'])
            msg = '{}\n\n{}\n\n'.format(caption, video_url)
            try:
                telegram.send_msg(msg)
                push_to_db(video['id'], __channel__.channel_id)
            except:
                pass


def main():
    channels = load_channels(channel_list_file_path)
    [watch_channel(channel) for channel in channels]


if __name__ == "__main__":
    main()
