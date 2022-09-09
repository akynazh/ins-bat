## Introduction

You can run `ins.py` to download saved posts in your instagram account.

The downloaded posts will be recorded to prevent the script from downloading them again.

If you login successfully, the script will save the session in session file, which will reduce the time to login next time.

## Prerequisites

- python3
- pip
- git (optional, you can also download the repo)

## Installation

```bash
git clone https://github.com/akynazh/INSBatchDownloader.git
pip3 install instaloader
cd InsBatchAutoDownloader
```

## Usage

### Edit {save_dir}/record.json

- {save_dir} is the directory where you save files.
- username: your instagram username
- password: your instagram password
- interval: download interval, recommand >= 15
- downloaded: the downloaded posts' shortcodes

```json
{
    "username": "", 
    "password": "", 
    "interval": 15, 
    "downloaded": []
}
```

### Start to download

```
nohup python3 ~/ins.py -d /ins &
```

If you are blocked by instagram or change your password in instagram, you should remove the session file: {save_dir}/sessions/session-{username}.

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)