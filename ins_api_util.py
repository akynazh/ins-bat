import json
import os
from instagram_private_api import Client


def load_record(SAVE_DIR):
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    RECORD_FILE = SAVE_DIR + '/record.json'
    try:
        if os.path.exists(RECORD_FILE):
            with open(RECORD_FILE, 'r') as f:
                RECORD = json.load(f)
            return True, RECORD
        else:  # record file does not exist, create and write basic data
            print(f'can not find {RECORD_FILE}, create it')
            with open(RECORD_FILE, 'w') as f:
                default_record = {
                    'username': '',
                    'password': '',
                    'tg_bot_token': '',
                    'tg_chat_id': '',
                    'downloaded': [],
                    'following': []
                }
                json.dump(default_record, f, separators=(',', ': '), indent=4)
                print('please edit record.json first')
            return False, None
    except Exception as e:
        print(f'fail to load record, error: {e}')
        return False, None

def update_record(SAVE_DIR, RECORD):
    RECORD_FILE = SAVE_DIR + '/record.json'
    try:
        with open(RECORD_FILE, 'w') as f:
            json.dump(RECORD, f, separators=(',', ': '), indent=4)
            print(f'mission success')
    except Exception as e:
        print(f'fail to renew the record, error: {e}')

def login(RECORD):
    username = RECORD['username']
    password = RECORD['password']
    if str(RECORD['proxy']).strip() != '':
        proxy = RECORD['proxy']
        api = Client(username, password, proxy=proxy)
    else:
        api = Client(username, password)
    return api