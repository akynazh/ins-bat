import instaloader
import json
import os
import time
import argparse


class InsBatchAutoDownloader:

    def __init__(self):
        global save_dir
        self.save_dir = save_dir
        self.loader = instaloader.Instaloader(quiet=True, download_video_thumbnails=False,
                                              save_metadata=False, post_metadata_txt_pattern="", request_timeout=30.0)
        self.record_file = self.save_dir + "/record.json"
        self.init_flag = False # load record successfully or not
        try:
            # load record
            if os.path.exists(self.record_file):
                with open(self.record_file, "r") as f:
                    self.record = json.load(f)
                self.username = self.record["username"] if "username" in self.record else ""
                self.password = self.record["password"] if "password" in self.record else ""
                self.interval = self.record["interval"] if "interval" in self.record else 15
                self.downloaded = self.record["downloaded"] if "downloaded" in self.record else []
                # if has wrong record
                if self.username == "" or self.password == "" or self.interval < 0:
                    log("wrong record")
                else:
                    self.session_file = self.save_dir + "/sessions/session-" + self.username
                    # successfully initial flag
                    self.init_flag = True
            else:
                # record file does not exist, create and write basic data
                with open(self.record_file, "w") as f:
                    default_record = {
                        'username': '', 'password': '', 'interval': 15, 'downloaded': []}
                    json.dump(default_record, f, separators=(
                        ', ', ': '), indent=4)
                    log("edit record.json first")
        except Exception as e:
            log(f"initial fail, error: {e}")
        except KeyboardInterrupt:
            log("exit successfully")
            exit(0)

    def login(self) -> bool:
        log("try to login as " + self.username + "...")
        try:
            # if session file exists
            if os.path.exists(self.session_file):
                log("find session, try to load session...")
                self.loader.load_session_from_file(
                    self.username, self.session_file)
            # login with password and save session
            else:
                log("find no session, try to login with password...")
                self.loader.login(self.username, self.password)
                try:
                    self.loader.save_session_to_file(self.session_file)
                except Exception as e:
                    log(f"fail to save session, error: {e}")
            return True
        except Exception as e:
            log(f"login fail, error: {e}")
            return False
        except KeyboardInterrupt:
            log("exit successfully")
            exit(0)

    def download(self):
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
            if len(new_posts_code) > 0:
                # download new posts
                log("find new posts, start to download...")
                os.chdir(self.save_dir)
                save_count = 0
                fail_count = 0
                for code in new_posts_code:
                    post = instaloader.Post.from_shortcode(
                        self.loader.context, code)
                    if self.loader.download_post(post, "ins_saved"):
                        log(f"download success, shortcode: {code}")
                        self.downloaded.append(code)
                        save_count += 1
                    else:
                        log(f"download fail, shortcode: {code}")
                        fail_count += 1
                log(
                    f"download completes, save count: {save_count}, fail count: {fail_count}")
            else:
                # no new posts
                log("find no new posts, wait for next try")
        except Exception as e:
            log(f"error happen: {e}")
        except KeyboardInterrupt:
            log("exit successfully")
            exit(0)
        finally:
            # renew record
            self.record["downloaded"] = self.downloaded
            try:
                with open(self.record_file, "w") as f:
                    json.dump(self.record, f, separators=(
                        ', ', ': '), indent=4)
            except Exception as e:
                log(f"renew record fail, error: {e}")

# print and log
def log(msg):
    global save_dir

    mmsg = "********** " + \
        time.strftime("%Y-%m-%d_%H-%M-%S_",
                      time.localtime(time.time())) + ": " + msg
    with open(save_dir + "/log.txt", "a") as f:
        if msg == "":
            print()
            f.write("\n")
        else:
            print(mmsg)
            f.write(mmsg + "\n")


if __name__ == "__main__":
    # get the save directory
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", type=str, default=os.getcwd() +
                        "/ins", help="the directory to save files, should be absolute path")
    args = parser.parse_args()
    save_dir = args.dir
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    log("##### Start InsBatchAutoDownload #####")
    log("files will be saved to: " + save_dir)

    # start to download
    log("init and load record...")
    ins = InsBatchAutoDownloader()
    if ins.init_flag:
        log("init and load record successfully")
        if ins.login():
            log("login successfully")
            while True:
                log("### DOWNLOAD PROCESS START ###")
                ins.download()
                log("### DOWNLOAD PROCESS END ###")
                log("")
                try:
                    time.sleep(ins.interval * 60)
                except KeyboardInterrupt:
                    log("exit successfully")
                    break