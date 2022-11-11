import instaloader
import os
import sys
import argparse
import logging
import threading
import instaloader.exceptions as ins_exceptions
import ins_util_telebot
import ins_util_recorder

class Logger:
    def __init__(self, log_file=None, log_level=logging.DEBUG):
        self.logger = logging.getLogger()
        if log_file != None:
            self.logger.addHandler(self.get_file_handler(file=log_file))
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(log_level)

    def get_file_handler(self, file):
        file_handler = logging.FileHandler(file)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        return file_handler

class MyInstaloader:
    def __init__(self):
        self.loader = instaloader.Instaloader(quiet=True,
                                              download_video_thumbnails=False,
                                              save_metadata=False,
                                              post_metadata_txt_pattern='',
                                              request_timeout=15.0,
                                              max_connection_attempts=3)
        self.record = RECORD
        self.username = RECORD['username']
        self.password = RECORD['password']
        self.downloaded = RECORD['downloaded']
        self.session_file = f'{SAVE_DIR}/session-{self.username}'
        self.lock = threading.Lock()
        self.saved_count = 0

    def login(self):
        LOG.info(f'try to login as {self.username}...')
        if os.path.exists(self.session_file) and REMOVE_SESSION:
            os.remove(self.session_file)
            LOG.info(f'remove old session: {self.session_file}.')
        try:
            if os.path.exists(self.session_file):
                LOG.info(f'find session file: {self.session_file}, try to load session...')
                self.loader.load_session_from_file(self.username, self.session_file)
            else:
                self.loader.login(self.username, self.password)
                self.loader.save_session_to_file(self.session_file)
            LOG.info('login successfully.')
            return True
        
        except ins_exceptions.TwoFactorAuthRequiredException:
            two_factor_code = input("Enter 2FA Code: ")
            self.loader.two_factor_login(two_factor_code)
            self.loader.save_session_to_file(self.session_file)
            LOG.info('login successfully.')
            return True
        except ins_exceptions.InvalidArgumentException:
            LOG.error('username does not exist.')
            return False
        except ins_exceptions.BadCredentialsException:
            LOG.error('password is wrong, try to remove the session file or modify your password.')
            return False
        except Exception as e:
            LOG.error(f'error occurred: {e}.')
            return False
        except KeyboardInterrupt:
            LOG.info('exit successfully.')
            exit(0)
            
    def download_from_code(self, code):
        post = instaloader.Post.from_shortcode(self.loader.context, code)
        self.loader.download_post(post, 'ins_saved')
        LOG.info(f'download successfully, code: {code}.')
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
                LOG.info('find new posts, start to download...')
                os.chdir(SAVE_DIR)
                download_threads = []
                for code in new_posts_code:
                    t = threading.Thread(target=self.download_from_code, args=(code,))
                    download_threads.append(t)
                    t.start()
                for t in download_threads:
                    t.join()
        except Exception as e:
            error_occurred = True
            LOG.error(f'error occurred: {e}.')
        except KeyboardInterrupt:
            LOG.info('exit successfully.')
            exit(0)
        finally:
            msg = f'[Instagram] downloading process completed, total count: {total_count}, saved count: {self.saved_count}, error occurred: {error_occurred} ^-^'
            LOG.info(msg)
            TeleBot.send_msg(msg)
            if self.saved_count > 0:  # if have saved new posts, log and renew record.
                self.record['downloaded'] = self.downloaded
                Recorder.update_record(new_record=self.record)

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
        help='If exists, send the downloaded files to your telegram chat which is specified in record.json and remove those files.'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = ins_parse_args()
    SAVE_DIR = args.dir
    REMOVE_SESSION = args.update
    PATH_RECORD_FILE = SAVE_DIR + '/record.json'
    PATH_MEDIA_DIR = SAVE_DIR + '/ins_saved'
    PATH_LOG_FILE = SAVE_DIR + '/log.txt'
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    LOG = Logger(log_file=PATH_LOG_FILE, log_level=logging.INFO).logger
    Recorder = ins_util_recorder.Recorder(PATH_RECORD_FILE)

    load_success, RECORD = Recorder.load_record()
    if load_success:
        if str(RECORD['proxy']).strip() != '':# add proxy
            proxy = RECORD['proxy']
            os.environ['http_proxy'] = proxy
            os.environ['https_proxy'] = proxy
        TeleBot = ins_util_telebot.TeleBot(RECORD, PATH_MEDIA_DIR)
        MyInstaloader = MyInstaloader()
        if MyInstaloader.login():
            MyInstaloader.download()
            TeleBot.send_medias()
        else:
            msg = '[Instagram] fail to login >_<'
            LOG.error(msg)
            TeleBot.send_msg(msg)
    else:
        LOG.error('fail to load record >_<')