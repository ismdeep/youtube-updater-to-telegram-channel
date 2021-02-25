import os
import requests
import json


class VideoInfo(object):
    video_id = None
    video_title = None
    publish_time = None
    is_at_premiere = False  # 是否为预播

    def __init__(self):
        pass

    def __str__(self):
        return "[{}, {}, {}]".format(self.video_id, self.video_title, self.publish_time)


class ChannelInfo(object):
    channel_id = None
    channel_title = None

    def __init__(self, __channel_id__, __channel_title__):
        self.channel_id = __channel_id__
        self.channel_title = __channel_title__

    def __str__(self):
        return "[{}, {}]".format(self.channel_id, self.channel_title)


def remove_local_mp3(__video_id__):
    file_name = "{}.mp3".format(__video_id__)
    if os.path.exists(file_name) and os.path.isfile(file_name):
        os.remove(file_name)


def download_mp3(__youtube_dl__, __video_id__):
    os.system(
        "{} "
        "-x "
        "--audio-format mp3 "
        "https://www.youtube.com/watch?v={} "
        "-o {}.mp3 "
        ">/dev/null "
        "2>/dev/null".format(__youtube_dl__, __video_id__, __video_id__))


def get_video_info(__video_id__) -> VideoInfo:
    video_url = "https://www.youtube.com/watch?v={}".format(__video_id__)
    content = requests.get(
        url=video_url,
        headers={
            'Accept-Language': 'en-US,en;'
                               'q=0.9,zh-TW;'
                               'q=0.8,zh-CN;'
                               'q=0.7,zh;'
                               'q=0.6,ja;'
                               'q=0.5,ko;'
                               'q=0.4',
            'User-Agent': 'Mozilla/5.0 '
                          '(Macintosh; Intel Mac OS X 10_14_6) '
                          'AppleWebKit/537.36 '
                          '(KHTML, like Gecko) '
                          'Chrome/88.0.4324.96 '
                          'Safari/537.36'
        }
    ).text
    print(content)
    is_at_premiere_flag = content.find("Premiere in progress.") >= 0 or content.find("Premieres in") >= 0
    publish_time = content[content.find('''"publishDate":"''') + len('''"publishDate":"'''):]
    publish_time = publish_time[:publish_time.find('''"''')]
    title = content[content.find('''"><title>''') + len('''"><title>'''):]
    title = title[:title.find(" - YouTube</title>")]
    video_info = VideoInfo()
    video_info.video_id = __video_id__
    video_info.publish_time = publish_time
    video_info.video_title = title
    video_info.is_at_premiere = is_at_premiere_flag
    return video_info


def get_all_videos(data, videos: []):
    if isinstance(data, dict) and 'gridVideoRenderer' in data:
        videos.append(data)
    elif isinstance(data, list):
        for item in data:
            get_all_videos(item, videos)
    elif isinstance(data, dict):
        for key in data:
            get_all_videos(data[key], videos)
    else:
        pass


def get_latest_videos(__channel_id__):
    req = requests.get(url="https://www.youtube.com/channel/{}".format(__channel_id__))
    content = req.text
    data = None
    for item in content.splitlines():
        if item.find('var ytInitialData =') >= 0:
            item = item[item.find('var ytInitialData =') + len('var ytInitialData ='):]
            item = item[:item.find(';</script><link')]
            data = json.loads(item)
    videos = []
    get_all_videos(data, videos)
    results = []
    for video in videos:
        results.append({
            'id': video['gridVideoRenderer']['videoId'],
            'title': video['gridVideoRenderer']['title']['simpleText']
        })
    return results
