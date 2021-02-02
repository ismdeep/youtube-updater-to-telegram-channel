import os


def remove_local_mp3(__video_id__):
    file_name = "{}.mp3".format(__video_id__)
    if os.path.exists(file_name) and os.path.isfile(file_name):
        os.remove(file_name)


def download_mp3(__video_id__):
    os.system(
        "youtube-dl "
        "-x "
        "--audio-format mp3 "
        "https://www.youtube.com/watch?v={} -o {}.mp3 >/dev/null 2>/dev/null".format(__video_id__, __video_id__))
