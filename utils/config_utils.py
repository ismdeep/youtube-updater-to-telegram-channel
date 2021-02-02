from utils.youtube_utils import ChannelInfo


def load_channels(__file_path__):
    channel_list = []
    with open(__file_path__) as f:
        for line in f:
            line = line.strip()
            if len(line.split()) <= 0:
                continue
            channel_id = line.split()[0].strip()
            if len(channel_id) > 0:
                channel_list.append(ChannelInfo(
                    channel_id,
                    line[len(channel_id):].strip()
                ))
    return channel_list
