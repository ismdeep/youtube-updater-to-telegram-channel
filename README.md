# YouTube Updater to Telegram Channel



This is program is simply to Keep YouTube Channel Videos up-to-date, and push to up-to-date videos to telegram channel.



## How to use?

1. First, create a `data` folder. We will have these files.

   1. `anon.session` : You may copy it from somewhere or generate it with Python `telethon` with the tutorials from web.

   2. `news_list.txt` : YouTube channel list format as below:

      ```
      UC7c3Kb6jYCRj4JOHHZTxKsQ    GitHub
      UCAuUUnT6oDeKwE6v1NGQxug    TED
      UCLA_DiR1FfKNvjuUpBHmylQ    NASA
      ```

   3. `redis.json` : Redis config as below.

      ```
      {
        "host": "localhost",
        "port": 6379
      }
      ```

   4. `telegram_bot.json` : Telegram config as below:

      ```
      {
        "api_id": ,
        "api_hash": "",
        "channel_share_link": "https://t.me/joinchat/xxxxxx"
      }
      ```

2. Run.

   ```
   python3 youtube_updater.py <data-folder-path> [--save-only]
   ```

   If you just want to save video_ids to redis, you may use `--save-only` argument, this won't push video to telegram channel. You can use it at the first time.

3. Tips

   Setup a cron on linux, then you can get your youtube channel updater up-to-date.



