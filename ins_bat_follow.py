import ins_api_util
import sys
import argparse

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-d', type=str, default=f'{sys.path[0]}', help='the directory to save files, should be absolute path')
    args = parser.parse_args()
    SAVE_DIR = args.dir
    # load record
    success, RECORD = ins_api_util.load_record(SAVE_DIR)
    if (success):
        # login
        api = ins_api_util.login(RECORD)
        # follow
        following_list = RECORD['following']
        for user_id in following_list:
            print(f'create friendship with {user_id}')
            api.friendships_create(user_id)