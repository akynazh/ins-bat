import os
import sys
import json
import argparse
import logging
import threading
import instaloader
import instaloader.exceptions as ins_exceptions
import ins_telebot

class Logger:
    def __init__(self, log_level):
        self.logger = logging.getLogger()
        self.logger.addHandler(self.get_file_handler(PATH_LOG_FILE))
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(log_level)

    def get_file_handler(self, file):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        return file_handler

def load_record():
    try:
        if os.path.exists(PATH_RECORD_FILE):
            with open(PATH_RECORD_FILE, 'r') as f:
                record = json.load(f)
            if record['username'].strip() == '' or record['password'].strip() == '':
                LOG.info('Please specify your username and password~')
                return False, None
            return True, record
        else:  # record file does not exist, create and write basic data
            LOG.error('Record file does not exist, create it. Please edit it first.')
            with open(PATH_RECORD_FILE, 'w') as f:
                default_record = {
                    'username': '',
                    'password': '',
                    'use_tg_bot': 0,
                    'tg_bot_token': '',
                    'tg_chat_id': '',
                    'use_proxy': 0,
                    'proxy_addr': '',
                    'downloaded': [],
                }
                json.dump(default_record, f, separators=(',', ': '), indent=4)
            return False, None
    except Exception as e:
        LOG.error(e)
        return False, None

class MyInstaloader:
    def __init__(self, telebot:ins_telebot.TeleBot=None):
        self.telebot = telebot
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
        self.session_file = f'{PATH_SAVE_DIR}/session-{self.username}'
        self.lock = threading.Lock()
        self.saved_count = 0

    def login(self):
        LOG.info(f'Try to login as {self.username}...')
        if os.path.exists(self.session_file) and OP_REMOVE_SESSION:
            os.remove(self.session_file)
            LOG.info(f'Remove old session: {self.session_file}.')
        try:
            if os.path.exists(self.session_file):
                LOG.info(f'Find session file: {self.session_file}, try to load session...')
                self.loader.load_session_from_file(self.username, self.session_file)
            else:
                self.loader.login(self.username, self.password)
                self.loader.save_session_to_file(self.session_file)
            LOG.info('Login successfully.')
            return True
        except ins_exceptions.TwoFactorAuthRequiredException:
            two_factor_code = input("Enter 2FA Code: ")
            self.loader.two_factor_login(two_factor_code)
            self.loader.save_session_to_file(self.session_file)
            LOG.info('Login successfully.')
            return True
        except ins_exceptions.InvalidArgumentException:
            LOG.error('Username does not exist.')
            return False
        except ins_exceptions.BadCredentialsException:
            LOG.error('Password is wrong, try to remove the session file or modify your password.')
            return False
        except Exception as e:
            LOG.error(f'Error occurred: {e}.')
            return False
        except KeyboardInterrupt:
            LOG.info('Exit successfully.')
            exit(0)
            
    def download_from_code(self, code):
        post = instaloader.Post.from_shortcode(self.loader.context, code)
        self.loader.download_post(post, MEDIA_DIR_NAME)
        LOG.info(f'Download successfully, code: {code}.')
        self.lock.acquire()
        self.downloaded.append(code)
        self.saved_count += 1
        self.lock.release()
        
    def download(self):
        total_count = 0
        error_occurred = False
        try:
            profile = instaloader.Profile.from_username(self.loader.context, self.username)
            # get saved posts now
            now_posts = profile.get_saved_posts()
            now_posts_code = []
            for post in now_posts:
                now_posts_code.append(post.shortcode)
            # get new posts
            new_posts_code = list(set(now_posts_code).difference(set(self.downloaded)))
            if len(new_posts_code) > 0:
                total_count = len(new_posts_code)
                LOG.info('Find new posts, start to download...')
                os.chdir(PATH_SAVE_DIR)
                download_threads = []
                for code in new_posts_code:
                    t = threading.Thread(target=self.download_from_code, args=(code,))
                    download_threads.append(t)
                    t.start()
                for t in download_threads:
                    t.join()
        except Exception as e:
            error_occurred = True
            LOG.error(f'Error occurred: {e}.')
        except KeyboardInterrupt:
            LOG.info('Exit successfully.')
            exit(0)
        finally:
            msg = f'[Instagram] Downloading process completed, total count: {total_count}, saved count: {self.saved_count}, error occurred: {error_occurred} ^-^'
            LOG.info(msg)
            if USE_TG_BOT == 1: self.telebot.send_msg(msg)
            if self.saved_count > 0:  # if have saved new posts, log and renew record.
                self.record['downloaded'] = self.downloaded
                with open(PATH_RECORD_FILE, 'w') as f:
                    json.dump(self.record, f, separators=(',', ': '), indent=4)

def ins_parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dir',
        '-d',
        type=str,
        default=f'{sys.path[0]}',
        help='Specify the directory to save files and load files, should be absolute path, if not specified, \
        the default value is the directory where `ins.py` locates in.')
    parser.add_argument(
        '--update',
        '-u',
        action='store_true',  # default False
        help='If exists, remove the old session file.')
    parser.add_argument(
        '--send',
        '-s',
        action='store_true',
        help='If exists, send the downloaded files to your telegram chat which is specified in record.json and remove those files. (Prerequisite: use telegram bot)'
    )
    return parser.parse_args()

def try_to_add_proxy():
    if str(RECORD['proxy_addr']).strip() != '':
        proxy = RECORD['proxy_addr']
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy
        LOG.info('Add proxy successfully.')
    else: 
        LOG.error('Fail to add proxy.')
        
if __name__ == '__main__':
    args = ins_parse_args()
    PATH_SAVE_DIR = args.dir
    OP_REMOVE_SESSION = args.update
    OP_TG_BOT_SEND = args.send
    
    if not os.path.exists(PATH_SAVE_DIR):
        os.makedirs(PATH_SAVE_DIR)
    
    MEDIA_DIR_NAME = 'ins_saved'
    PATH_RECORD_FILE = PATH_SAVE_DIR + '/record.json'
    PATH_LOG_FILE = PATH_SAVE_DIR + '/ins_log.txt'
    PATH_MEDIA_DIR = PATH_SAVE_DIR + '/' + MEDIA_DIR_NAME
        
    LOG = Logger(log_level=logging.INFO).logger
    load_success, RECORD = load_record()
    if load_success:
        USE_PROXY = RECORD['use_proxy']
        USE_TG_BOT = RECORD['use_tg_bot']
        if USE_PROXY == 1: try_to_add_proxy()
        if USE_TG_BOT == 1:
            telebot = ins_telebot.TeleBot(logger=LOG, record=RECORD, path_media_dir=PATH_MEDIA_DIR)
            my_instaloader = MyInstaloader(telebot)
        else:
            my_instaloader = MyInstaloader()
        if my_instaloader.login():
            # my_instaloader.download()
            if USE_TG_BOT == 1 and OP_TG_BOT_SEND:
                telebot.send_medias()
        else:
            msg = '[Instagram] Fail to login >_<'
            LOG.error(msg)
            if USE_TG_BOT == 1: telebot.send_msg(msg)
    else:
        LOG.error('Fail to load record >_<')
    LOG.info("Program exited successfully.")