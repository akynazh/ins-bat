import instaloader
import json
import os
import argparse
import logging
import requests
import instaloader.exceptions as ins_exceptions


class Logger:
    # initial logger
    def __init__(self, log_file=None, log_level=logging.DEBUG):
        self.logger = logging.getLogger()
        if log_file != None:
            self.logger.addHandler(self.get_file_handler(file=log_file))
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(log_level)

    # save log to file
    def get_file_handler(self, file):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        return file_handler


class InsBatchAutoDownloader:

    def __init__(self):
        self.loader = instaloader.Instaloader(quiet=True,
                                              download_video_thumbnails=False,
                                              save_metadata=False,
                                              post_metadata_txt_pattern='',
                                              request_timeout=15.0,
                                              max_connection_attempts=3)
        self.record = RECORD
        self.username = self.record['username']
        self.password = self.record['password']
        self.downloaded = self.record['downloaded']
        self.session_file = f'{SAVE_DIR}/session-{self.username}'

    def login(self):
        LOG.info(f'try to login as {self.username}...')
        if os.path.exists(self.session_file) and REMOVE_SESSION:
            os.remove(self.session_file)
        try:
            if os.path.exists(self.session_file):
                LOG.info(
                    f'find session file: {self.session_file}, try to load session...'
                )
                self.loader.load_session_from_file(self.username,
                                                   self.session_file)
            else:
                self.loader.login(self.username, self.password)
                self.loader.save_session_to_file(self.session_file)
            LOG.info('login successfully')
            return True
        except ins_exceptions.InvalidArgumentException:
            LOG.warn('username does not exist')
            return False
        except ins_exceptions.BadCredentialsException:
            LOG.warn(
                'password is wrong, try to remove the session file or modify your password'
            )
            return False
        except Exception as e:
            LOG.error(f'fail to login, error: {e}')
            return False
        except KeyboardInterrupt:
            LOG.info('exit successfully')
            exit(0)

    def download(self):
        saved_count = 0
        total_count = 0
        error_occurred = False
        try:
            # get profile
            profile = instaloader.Profile.from_username(
                self.loader.context, self.username)
            # get saved posts now
            now_posts = profile.get_saved_posts()
            now_posts_code = []
            for post in now_posts:
                now_posts_code.append(post.shortcode)
            # get new posts_code
            new_posts_code = list(
                set(now_posts_code).difference(set(self.downloaded)))
            if len(new_posts_code) > 0:  # have new posts
                total_count = len(new_posts_code)
                LOG.info('find new posts, start to download...')
                os.chdir(SAVE_DIR)
                for code in new_posts_code:
                    post = instaloader.Post.from_shortcode(
                        self.loader.context, code)
                    self.loader.download_post(post, 'ins_saved')
                    LOG.info(f'download successfully, shortcode: {code}')
                    self.downloaded.append(code)
                    saved_count += 1
        except Exception as e:
            error_occurred = True
            LOG.error(f'error happens: {e}')
        except KeyboardInterrupt:
            LOG.info('exit successfully')
            exit(0)
        finally:
            msg = f'download completed, total count: {total_count}, saved count: {saved_count}, error occurred: {error_occurred} ^-^'
            LOG.info(msg)
            tg_bot_send_msg(msg)
            if saved_count > 0:  # if have saved new posts, log and renew record.
                # renew record
                self.record['downloaded'] = self.downloaded
                try:
                    with open(RECORD_FILE, 'w') as f:
                        json.dump(self.record,
                                  f,
                                  separators=(', ', ': '),
                                  indent=4)
                except Exception as e:
                    LOG.error(f'fail to renew the record, error: {e}')

def load_record():
    global RECORD
    try:
        if os.path.exists(RECORD_FILE):
            with open(RECORD_FILE, 'r') as f:
                RECORD = json.load(f)
            for key in ['username', 'password', 'downloaded']:
                if key not in RECORD:
                    LOG.error(f'fail to load record: lost key: {key}')
                    return False
            if isinstance(RECORD['downloaded'], list) and str(RECORD['username']).strip() != '' and \
                str(RECORD['password']).strip() != '':
                return True
        else:  # record file does not exist, create and write basic data
            LOG.error(f'can not find {RECORD_FILE}, create it')
            with open(RECORD_FILE, 'w') as f:
                default_record = {
                    'username': '',
                    'password': '',
                    "tg_bot_token": "",
                    "tg_user_id": "",
                    'downloaded': []
                }
                json.dump(default_record, f, separators=(', ', ': '), indent=4)
                LOG.error('please edit record.json first')
            return False
    except Exception as e:
        LOG.error(f'fail to load record, error: {e}')
        return False


def tg_bot_send_msg(msg):
    tg_bot_token = RECORD['tg_bot_token'] if 'tg_bot_token' in RECORD else ''
    tg_user_id = RECORD['tg_user_id'] if 'tg_user_id' in RECORD else ''
    if tg_bot_token != '' and tg_user_id != '':
        r = requests.get(
            f'https://api.telegram.org/bot{tg_bot_token}/sendMessage',
            params={
                'text': f'{msg}',
                'chat_id': f'{tg_user_id}'
            })
        ok = r.json()['ok']
        if not ok:
            LOG.error(f'tg_bot: fail to send msg')


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dir',
        type=str,
        default=f'{os.getcwd()}/ins',
        help='the directory to save files, should be absolute path')
    parser.add_argument(
        '--update',
        action='store_true',  # default False
        help='if `--update` exists, remove the old session file')
    args = parser.parse_args()

    # set basic values
    SAVE_DIR = args.dir
    REMOVE_SESSION = args.update
    RECORD_FILE = SAVE_DIR + '/record.json'
    LOG_FILE = SAVE_DIR + '/ins_log.txt'
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # initial logger
    LOG = Logger(log_file=LOG_FILE, log_level=logging.INFO).logger

    LOG.info('### START ###')
    RECORD = {}
    if load_record():  # load successfully
        ins = InsBatchAutoDownloader()  # initial InsBatchAutoDownloader
        if ins.login():  # if login successfully
            ins.download()  # start to download
        else:
            tg_bot_send_msg('fail to login =_=')
    LOG.info('###  END  ###')