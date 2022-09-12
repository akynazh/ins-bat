## Introduction

You can use this script to download saved posts in your instagram account.

The downloaded posts will be recorded to prevent the script from downloading them again.

## Prerequisites

- python3
- pip3
- proxy (optional, only if instagram is blocked in your area)

## Installation

```bash
git clone https://github.com/akynazh/INSBatchDownloader.git # or download this repo
pip3 install instaloader
```

## Usage

### Edit `{save_dir}/record.json`

- `{save_dir}` is the directory where you save files.
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

Then the posts will be downloaded to `{save_dir}/ins_saved`.

`-d {save_dir}` is optional, the default value is `{current_dir}/ins`.

You may let the script run in the background and not to hang up when closing the terminal:

If you deploy the script on linux, just run:

```bash
nohup python ins.py -d {save_dir} &
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

If you are blocked by instagram or find that you can not get the correct data, try to restart the script.

If you change your password in instagram, you should stop the script, modify the password in `record.json` and then run the script again.

You can read log in `{save_dir}/log.txt`.

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)
