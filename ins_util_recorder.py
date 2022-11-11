import json
import os

class Recorder:
    def __init__(self, path_record_file):
        self.path = path_record_file
        
    def update_record(self, new_record):
        with open(self.path, 'w') as f:
            json.dump(new_record, f, separators=(',', ': '), indent=4)
            
    def create_record_file(self):
        with open(self.path, 'w') as f:
            default_record = {
                'username': '',
                'password': '',
                'tg_bot_token': '',
                'tg_chat_id': '',
                'proxy': '',
                'downloaded': [],
            }
            json.dump(default_record, f, separators=(',', ': '), indent=4)
            
    def load_record(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r') as f:
                    record = json.load(f)
                return True, record
            else:  # record file does not exist, create and write basic data
                self.create_record_file()
                return False, None
        except Exception:
            return False, None