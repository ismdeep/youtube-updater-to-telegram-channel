import requests
import json
import sys
import os

BASE = "https://www.googleapis.com/youtube/v3"
APP_KEY = os.environ.get('YOUTUBE_APP_KEY')


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
    channel_list_file_path = sys.argv[1]
    videos_list = []
    channels_list = []
    with open(channel_list_file_path) as f:
        for line in f:
            channels_list.append(line.split()[0].strip())

    for channel_id in channels_list:
        channel_latest_videos = get_latest_videos_from_channel(channel_id)
        for item in channel_latest_videos:
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            video_url = "https://www.youtube.com/watch?v={}".format(video_id)
            duration = item["duration"]
            time_published = item["snippet"]["publishedAt"]
            print(time_published, title, video_url, duration)
        videos_list += channel_latest_videos


if __name__ == "__main__":
    main()
