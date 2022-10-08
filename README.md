## Introduction

You can use this script to download saved posts in your instagram account.

The downloaded posts will be recorded to prevent the script from downloading them again.

After your first login, the script saves the session to file and the next time you login, the script will load the session from file.

Optionally, you can set a telegram bot to notify you about the downloading process, which is helpful if you set a timed task.

You can set a timedtask like the crontab on linux to execute this script regularly.

## Prerequisites

- python3
- pip3

## Installation

```bash
git clone https://github.com/akynazh/ins-bat # or download this repo
pip3 install instaloader
pip3 install pyTelegramBotAPI # optional, do it if you need a telegram bot to notify you
```

## Usage

### Edit `{save_dir}/record.json`

- `{save_dir}` is the directory where you save files.
- username: your instagram username
- password: your instagram password
- tg_bot_token: optional, your telegram bot's token
- tg_user_id: optional, your telegram id
- proxy: optional, set your proxy address, such as `http://127.0.0.1:7890` (you can also set your proxy to environment variable)
- downloaded: the downloaded posts' shortcodes

```json
{
    "username": "", 
    "password": "", 
    "tg_bot_token": "", 
    "tg_user_id": "",
    "proxy": "",
    "downloaded": []
}
```

### Run the script

About `ins.py`:

```
usage: ins.py [-h] [--dir DIR] [--update]

optional arguments:
  -h, --help  show this help message and exit
  --dir DIR   the directory to save files, should be absolute path
  --update    if `--update` exists, remove the old session file
```

You can just run:

```
python3 ins.py --dir {save_dir}
```

Then the posts will be saved in `{save_dir}/ins_saved`.

`--dir {save_dir}` is optional, the default value is `{current_dir}/ins`.

`--update` is optional too, if you fail to download new posts or load the session, you may add it to update the session.

You can read log in `{save_dir}/log.txt`.

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)
