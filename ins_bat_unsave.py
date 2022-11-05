import ins_api_util
from instagram_private_api_extensions import pagination
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
        # get all saved posts
        items = []
        for results in pagination.page(api.saved_feed, args={}):
            if results.get('items'):
                items.extend(results['items'])
        print(f'total: {len(items)}')
        # unsave posts
        for i, x in enumerate(items):
            media_id = items[i]['media']['pk']
            # code = items[i]['media']['code']
            api.unsave_photo(media_id)
            print(f'unsave: media_id={media_id}')