import instaloader
import json
import os
import time
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
        self.interval = self.record['interval']
        self.downloaded = self.record['downloaded']
        self.error_count = 0
        self.session_file = f'{SAVE_DIR}/session-{self.username}'
        self.first_download = True

    def login(self):
        LOG.info(f'try to login as {self.username}...')
        try:
            if os.path.exists(self.session_file):
                LOG.info(f'find session file: {self.session_file}, try to load session...')
                self.loader.load_session_from_file(self.username, self.session_file)
            else:
                self.loader.login(self.username, self.password)
                self.loader.save_session_to_file(self.session_file)
            LOG.info('login successfully')
            return True
        except ins_exceptions.InvalidArgumentException:
            LOG.info('username does not exist')
            exit(0)
        except ins_exceptions.BadCredentialsException:
            LOG.info('password is wrong, try to remove the session file or modify your password')
            exit(0)
        except ins_exceptions.ConnectionException as e:
            LOG.error(f'fail to login, error: {e}')
            return False
        except KeyboardInterrupt:
            LOG.info('exit successfully')
            exit(0)

    def download(self):
        saved_count = 0
        total_count = 0
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
                self.error_count = 0
        except Exception as e:
            LOG.error(f'error happens: {e}')
            self.error_count += 1
        except KeyboardInterrupt:
            LOG.info('exit successfully')
            exit(0)
        finally:
            if saved_count > 0:  # if have saved new posts, log and renew record.
                LOG.info(
                    f'download completed, total count: {total_count}, saved count: {saved_count}'
                )
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
            else:
                if self.first_download:
                    self.first_download = False
                    LOG.info(f'find no new posts to download, go to sleep for {self.interval} minutes...')


def load_record():
    try:
        if os.path.exists(RECORD_FILE):
            with open(RECORD_FILE, 'r') as f:
                record = json.load(f)
            for key in ['username', 'password', 'interval', 'downloaded']:
                if key not in record:
                    LOG.error(f'fail to load record: lost key: {key}')
                    return False, None
            if isinstance(record['downloaded'], list) and str(record['username']).strip() != '' and \
                str(record['password']).strip() != '' and int(record['interval']) >= 0:
                return True, record
        else:  # record file does not exist, create and write basic data
            LOG.error(f'can not find {RECORD_FILE}, create it')
            with open(RECORD_FILE, 'w') as f:
                default_record = {
                    'username': '',
                    'password': '',
                    'interval': 15,
                    "tg_bot_token": "",
                    "tg_user_id": "",
                    'downloaded': []
                }
                json.dump(default_record, f, separators=(', ', ': '), indent=4)
                LOG.error('please edit record.json first')
            return False, None
    except Exception as e:
        LOG.error(f'fail to load record, error: {e}')
        return False, None


def tg_bot_send_msg(msg):
    tg_bot_token = RECORD['tg_bot_token'] if 'tg_bot_token' in RECORD else ''
    tg_user_id = RECORD['tg_user_id'] if 'tg_user_id' in RECORD else ''
    if tg_bot_token == '' and tg_user_id == '':
        LOG.info('did not set a telegram bot')
        return
    r = requests.get(f'https://api.telegram.org/bot{tg_bot_token}/sendMessage',
                     params={
                         'text': f'{msg}',
                         'chat_id': f'{tg_user_id}'
                     })
    if r.status_code != 200: LOG.error('telegram bot fails to send messages')


def ok_sleep(minutes):
    try:
        time.sleep(60 * minutes)
    except KeyboardInterrupt:
        LOG.info('exit successfully')
        exit(0)


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dir',
        '-d',
        type=str,
        default=os.getcwd(),
        help='the directory to save files, should be absolute path')
    args = parser.parse_args()

    # set basic values
    SAVE_DIR = args.dir
    RECORD_FILE = SAVE_DIR + '/record.json'
    LOG_FILE = SAVE_DIR + '/ins_log.txt'
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # initial logger
    LOG = Logger(log_file=LOG_FILE, log_level=logging.INFO).logger
    LOG.info('[INSBATCHAUTODOWNLOADER-STARTED]')

    # load record
    load_success, RECORD = load_record()
    if load_success:  # load successfully
        # initial InsBatchAutoDownloader
        ins = InsBatchAutoDownloader()
        if ins.login():  # if login successfully
            # start to download
            while True:
                ins.download()
                # too many errors, login again
                if ins.error_count >= 4:
                    LOG.warn('download error count >= 4, try to login again')
                    login_fail_count = 0
                    while not ins.login():  # fail to login
                        login_fail_count += 1
                        if login_fail_count >= 3:  # always fail to login
                            LOG.error('login error count >= 3, try to remove session and login again')
                            if os.path.exists(ins.session_file): # try to remove session
                                os.remove(ins.session_file)
                            else: # totally fail to login
                                tg_bot_send_msg(
                                    '[INSBATCHAUTODOWNLOADER]: fail to login, please fix the fucking problem by yourself.'
                                )
                                exit(0)
                        LOG.info(
                            'fail to login, wait for 15 minutes and try to login again...')
                        ok_sleep(15)
                    ins.error_count = 0  # login successfully, set error count to 0 again
                ok_sleep(ins.interval)