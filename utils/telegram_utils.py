import json

from telethon.sync import TelegramClient
from telethon.sync import functions


class Telegram(object):
    app_id = None
    api_hash = None
    client = None
    channel = None

    def __init__(self):
        pass

    def load_config(self, __config_path__):
        f = open(__config_path__, 'r')
        config = json.load(f)
        f.close()
        self.api_id = config['api_id']
        self.api_hash = config['api_hash']
        channel_share_link = config['channel_share_link']
        session_path = config['session']
        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
        self.client.connect()
        self.channel = self.client.get_entity(channel_share_link)

    def send_msg(self, msg):
        self.client(functions.messages.SendMessageRequest(
            peer=self.channel,
            message=msg,
            no_webpage=False
        ))

    def send_mp3_file(self, __file_path__, __caption__):
        self.client.send_file(self.channel, __file_path__, caption=__caption__)
