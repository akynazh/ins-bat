## Introduction

You can use this script to download saved posts in your telegram account.

The downloaded posts will be recorded in `record.json`, so you can remove or move the downloaded posts in the download directory, the next time you run the script, the script won't download the posts that are recorded in `record.json`.If you want to download the downloaded posts again, you can remove `record.json`.

If you login successfully, the script will save the session in session file, which will reduce the time to login next time. If you change your password, you should remove the session file and login with password again. The session file's name is session-{your-username}.

## Installation

- Prerequisites
  - python3
  - pip

```bash
pip3 install instaloader
python ins.py {login_user_name}
```

## Usage

You should specify your {login_user_name} in the command.

The {root_path} is optional, default value is "ins". The {root_path} is the directory that stores record, download files, session files and logs.

```
python ins.py {login_user_name} {root_path}
```

## Thanks

- [Instaloader](https://github.com/instaloader/instaloader)