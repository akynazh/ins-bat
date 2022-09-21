## Introduction

You can use this script to download saved posts in your instagram account.

The downloaded posts will be recorded to prevent the script from downloading them again.

After your first login, the script saves the session to file and the next time you login, the script will load the session from file.

Optionally, you can set a telegram bot to send you the messages about the downloading process.

## Prerequisites

- python3
- pip3
- proxy (optional, only if instagram is blocked in your area)

## Installation

```bash
git clone https://github.com/akynazh/INSBatchDownloader.git # or download this repo
pip3 install instaloader
pip3 install pyTelegramBotAPI # optional, do it if you need a telegram bot to notify you
```

## Usage

### Edit `{save_dir}/record.json`

- `{save_dir}` is the directory where you save files.
- username: your instagram username
- password: your instagram password
- interval: download interval(unit: minute), recommand >= 15 minutes
- tg_bot_token: optional, your telegram bot's token
- tg_user_id: optional, your telegram id
- downloaded: the downloaded posts' shortcodes

```json
{
    "username": "", 
    "password": "", 
    "interval": 15, 
    "tg_bot_token": "", 
    "tg_user_id": "", 
    "downloaded": []
}
```

### Start the script

You can just run:

```
python3 ins.py -d {save_dir}
```

Then the posts will be downloaded to `{save_dir}/ins_saved`.

`-d {save_dir}` is optional, the default value is `{current_dir}/ins`.

You may let the script run in the background and not to hang up when closing the terminal:

If you deploy the script on linux, just run:

```bash
nohup python3 ins.py -d {save_dir} &
```

If you delpy the script on window, you can use vbs, edit `ins.vbs`:

```vb
Dim WshShell
Set WshShell=WScript.CreateObject("WScript.Shell")
iReturnCode=WshShell.Run("python3 ins.py -d {save_dir}", 0, TRUE)
```

then run:

```
wscript ins.vbs
```

## Remind

If you change your password in instagram, you should stop the script, modify the password in `{save_dir}/record.json` and remove the session file `{save_dir}/session-{username}`, and then restart the script.

If you are blocked by meta unfortunately, you may stop the script and try to restart the script after a few days.

You can read log in `{save_dir}/log.txt`.

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)
