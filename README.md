## Introduction

`ins.py`:

- download new saved posts in batches 
- save login session
- save downloaded posts
- a telegram bot, notify you about the result (it's useful if you set a timetask)

`ins_bat_follow.py` -> follow users in batches

`ins_get_following.py` -> get the users you are following in instagram

`ins_bat_unsave.py` -> unsave the posts in batches

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

optional, do it if you need the other scripts except `ins.py`:

```bash
pip3 install instagram_private_api_extensions
pip3 install instagram_private_api
```

## Usage

### Edit `{save_dir}/record.json`

`{save_dir}` is the directory where you save files.

- username: your instagram username
- password: your instagram password

optional:

- tg_bot_token: your telegram bot's token
- tg_chat_id: user id or group id
- proxy: set your proxy address, such as `http://127.0.0.1:7890` (you can also set your proxy to environment variable)

others: (no need to edit)

- downloaded: the downloaded posts' shortcodes
- following: the users you are following

```json
{
    "username": "", 
    "password": "", 
    "tg_bot_token": "", 
    "tg_chat_id": "",
    "proxy": "",
    "downloaded": [],
    "following": []
}
```

### Run the script `ins.py`

About `ins.py`:

```
usage: ins.py [-h] [--dir DIR] [--update]

options:
  -h, --help         show this help message and exit
  --dir DIR, -d DIR  the directory to save files, should be absolute path
  --update, -u       if `--update` exists, remove the old session file
```

You can just run:

```
python3 ins.py --dir {save_dir}
```

Then the posts will be saved in `{save_dir}/ins_saved`.

`--dir {save_dir}` is optional, the default value of {save_dir} is the directory where `ins.py` locates in.

`--update` is optional too, if you fail to download new posts or load the session, you may add it to update the session.

You can read log in `{save_dir}/log.txt`.

### Run the other scripts

```
usage: xxx.py [-h] [--dir DIR]

options:
  -h, --help         show this help message and exit
  --dir DIR, -d DIR  the directory to save files, should be absolute path
```

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)