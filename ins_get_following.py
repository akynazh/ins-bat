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
        username = RECORD['username']
        # get following users
        data = api.user_following(api.username_info(username)['user']['pk'], api.generate_uuid())
        following_list = RECORD['following']
        for user in data['users']:
            following_list.append(str(user['pk']))
        print(f'following count: {len(following_list)}')
        # save or update record
        RECORD['following'] = following_list
        ins_api_util.update_record(SAVE_DIR, RECORD)