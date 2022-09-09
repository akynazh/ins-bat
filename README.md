## Introduction

You can use this script to download saved posts in your instagram account.

The downloaded posts will be recorded to prevent the script from downloading them again.

If you login successfully, the script will save the session, which reduce the time to login next time.

## Prerequisites

- python3
- pip3

## Installation

```bash
git clone https://github.com/akynazh/INSBatchDownloader.git # or download this repo
pip3 install instaloader
```

## Usage

### Edit {save_dir}/record.json

- {save_dir} is the directory where you save files.
- username: your instagram username
- password: your instagram password
- interval: download interval(unit: minute), recommand >= 15 minutes
- downloaded: the downloaded posts' shortcodes

```json
{
    "username": "", 
    "password": "", 
    "interval": 15, 
    "downloaded": []
}
```

### Start the script

You can just run:

```
python ins.py -d {save_dir}
```

`-d {save_dir}` is optional, the default value is {current_dir}/ins.

You may let the script run in the background and not to hang up:

If you deploy the script on linux, just run:

```bash
nohup python ins.py -d {save_dir} &
```

If you delpy the script on window, you can use vbs, edit `ins.vbs`

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

If you are blocked by instagram or change your password in instagram, you should remove the session file: {save_dir}/sessions/session-{username},modify the password in record.json and then run the script.

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)