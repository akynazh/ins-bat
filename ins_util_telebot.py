import requests
import filetype
import os
import threading

class TeleBot:
    def __init__(self, record, path_media_dir):
        self.use_tg_bot = False
        self.tg_bot_token = record['tg_bot_token'] if 'tg_bot_token' in record else ''
        self.tg_chat_id = record['tg_chat_id'] if 'tg_chat_id' in record else ''
        self.path_media_dir = path_media_dir
        self.lock = threading.Lock()
        self.send_success_count = 0
        if self.tg_bot_token != '' and self.tg_chat_id != '':
            self.use_tg_bot = True

    def send_msg(self, msg):
        if self.use_tg_bot:
            r = requests.get(
                f'https://api.telegram.org/bot{self.tg_bot_token}/sendMessage',
                params={
                    'text': msg,
                    'chat_id': self.tg_chat_id
                })
            if not r.json()['ok']: return False
        return True
    
    def send_media(self, media_path):
        if self.use_tg_bot:
            with open(media_path, 'rb') as f:
                ft = filetype.guess_mime(media_path).split('/')[0]
                if ft == 'image': 
                    type = 'photo'
                    my_url = f'https://api.telegram.org/bot{self.tg_bot_token}/sendPhoto'
                elif ft == 'video': 
                    type = 'video'
                    my_url = f'https://api.telegram.org/bot{self.tg_bot_token}/sendVideo'
                r = requests.post(
                    url=my_url,
                    params={
                        'chat_id': self.tg_chat_id
                    },
                    files={type: f},
                )
            if not r.json()['ok']: return False
            self.lock.acquire()
            self.send_success_count += 1
            self.lock.release()
        return True

    def send_medias(self):
        if self.use_tg_bot:
            medias = os.listdir(self.path_media_dir)
            send_threads = []
            total_count = len(medias)
            if total_count > 0:
                for media in medias:
                    media_path = f'{self.path_media_dir}/{media}'
                    t = threading.Thread(target=self.send_media, args=(media_path,))
                    send_threads.append(t)
                    t.start()
                for t in send_threads:
                    t.join()
                self.send_msg(f'[Instagram] sending process completed, total count: {total_count}, success count: {self.send_success_count}.')