## Introduction

- download new saved posts in batches 
- save login session
- save downloaded posts
- a telegram bot, notify you about the result (it's useful if you set a timetask)
- a telegram bot, send you the downloaded posts
- support 2FA

## Prerequisites

- python3
- pip3

## Installation

```bash
git clone https://github.com/akynazh/ins-bat # or download this repo
pip3 install instaloader
```

optional, do it if you need a telegram bot to notify you:

```bash
pip3 install pyTelegramBotAPI
```

## Usage

### Edit `{save_dir}/record.json`

`{save_dir}` is the directory where you save files and load files.

- username: your instagram username
- password: your instagram password
- use_tg_bot: use telegram bot or not, 0: false, 1: true
- tg_bot_token: (prerequsite: use_tg_bot == 1) your telegram bot's token
- tg_chat_id: (prerequsite: use_tg_bot == 1) your telegram user id or group id
- use_proxy: use proxy or not, 0: false, 1: true
- proxy_addr: (prerequsite: use_proxy == 1) set your proxy address, such as `http://127.0.0.1:7890` (you can also set your proxy to environment variable)
- downloaded: the downloaded posts' shortcodes

```json
{
    "username": "",
    "password": "",
    "use_tg_bot": 0,
    "tg_bot_token": "",
    "tg_chat_id": "",
    "use_proxy": 0,
    "proxy_addr": "",
    "downloaded": []
}
```

### Run the script `ins.py`

About `ins.py`:

```
usage: ins.py [-h] [--dir DIR] [--update] [--send]

options:
  -h, --help         show this help message and exit
  --dir DIR, -d DIR  Specify the directory to save files and load files, should be absolute path, if not specified, the default value is 
                     the directory where `ins.py` locates in.
  --update, -u       If exists, remove the old session file.
  --send, -s         If exists, send the downloaded files to your telegram chat which is specified in record.json and 
                     remove those files. (Prerequisite: use telegram bot)
```

You can just run:

```
python3 ins.py --dir {save_dir}
```

The posts will be saved in `{save_dir}/ins_saved`.

You can read log in `{save_dir}/log.txt`.

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)