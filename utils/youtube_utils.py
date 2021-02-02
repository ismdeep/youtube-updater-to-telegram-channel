import os


def download_mp3(__video_id__):
    os.system(
        "/usr/local/bin/youtube-dl "
        "-x "
        "--audio-format mp3 "
        "https://www.youtube.com/watch?v={} -o {}.mp3".format(__video_id__, __video_id__))
