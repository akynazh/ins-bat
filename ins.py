import instaloader
import json
import os
import time
import argparse

def load_record(save_dir):
    record_file = save_dir + "/record.json"
    try:
        if os.path.exists(record_file):
            with open(record_file, "r") as f:
                record = json.load(f)
            for key in ["username", "password", "interval", "downloaded"]:
                if key not in record: 
                    log("fail to load record: lost key: " + key)
                    return False, None
            if isinstance(record["downloaded"], list) and record["username"] != "" and \
                record["password"] != "" and int(record["interval"]) >= 0:
                return True, record
        else: # record file does not exist, create and write basic data
            log("can not find " + record_file + ", create it")
            with open(record_file, "w") as f:
                default_record = {'username': '', 'password': '', 'interval': 15, 'downloaded': []}
                json.dump(default_record, f, separators=(', ', ': '), indent=4)
                log("please edit record.json first")
            return False, None
    except Exception as e:
        log(f"fail to load record, error: {e}")
        return False, None

def log(msg):
    global save_dir

    mmsg = "********** " + time.strftime("%Y-%m-%d_%H-%M-%S_", time.localtime(time.time())) + ": " + msg
    with open(save_dir + "/log.txt", "a") as f:
        if msg == "":
            print()
            f.write("\n")
        else:
            print(mmsg)
            f.write(mmsg + "\n")

class InsBatchAutoDownloader:

    def __init__(self, record, save_dir):
        self.save_dir = save_dir
        self.loader = instaloader.Instaloader(quiet=True, download_video_thumbnails=False,
                                              save_metadata=False, post_metadata_txt_pattern="", 
                                              request_timeout=15.0, max_connection_attempts=3)
        self.record = record
        self.record_file = save_dir + "/record.json"
        self.username = self.record["username"]
        self.password = self.record["password"]
        self.interval = self.record["interval"]
        self.downloaded = self.record["downloaded"]

    def login(self):
        log("try to login as " + self.username + "...")
        try:
            self.loader.login(self.username, self.password)
            log("login successfully")
            return True
        except Exception as e:
            log(f"login fail, error: {e}")
            return False
        except KeyboardInterrupt:
            log("exit successfully")
            exit(0)

    def download(self):
        save_count = 0
        total_count = 0
        try:
            # get profile
            profile = instaloader.Profile.from_username(self.loader.context, self.username)
            # get saved posts now
            now_posts = profile.get_saved_posts()
            now_posts_code = []
            for post in now_posts:
                now_posts_code.append(post.shortcode)
            # get new posts_code
            new_posts_code = list(set(now_posts_code).difference(set(self.downloaded)))
            if len(new_posts_code) > 0: # have new posts
                total_count = len(new_posts_code)
                log("find new posts, start to download...")
                os.chdir(self.save_dir)
                for code in new_posts_code:
                    # if save_count == 2: break # just for test
                    post = instaloader.Post.from_shortcode(self.loader.context, code)
                    self.loader.download_post(post, "ins_saved")
                    log(f"download success, shortcode: {code}")
                    self.downloaded.append(code)
                    save_count += 1
        except Exception as e:
            log(f"error happen: {e}")
        except KeyboardInterrupt:
            log("exit successfully")
            exit(0)
        finally:
            if save_count > 0: # if have saved new posts, log and renew record.
                log(f"download completes, total count: {total_count}, save count: {save_count}")
                # renew record
                self.record["downloaded"] = self.downloaded
                try:
                    with open(self.record_file, "w") as f:
                        json.dump(self.record, f, separators=(', ', ': '), indent=4)
                except Exception as e:
                    log(f"renew record fail, error: {e}")

if __name__ == "__main__":
    # get the directory to save files
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", type=str, default=os.getcwd() +
                        "/ins", help="the directory to save files, should be absolute path")
    args = parser.parse_args()
    save_dir = args.dir
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    log("^-^ InsBatchAutoDownload ^-^")
    load_success, record = load_record(save_dir) # load record
    if load_success: # load successfully
        ins = InsBatchAutoDownloader(record, save_dir) # initial InsBatchAutoDownloader
        if ins.login(): # if login successfully
            # start to download
            while True:
                ins.download()
                try:
                    time.sleep(ins.interval * 60) # wait for next try
                except KeyboardInterrupt:
                    log("exit successfully")
                    break