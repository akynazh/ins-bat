import instaloader
import json
import os
import time
import argparse


class InsBatchAutoDownloader:

    def __init__(self, save_dir):
        self.loader = instaloader.Instaloader(quiet=True, download_video_thumbnails=False,
                                              save_metadata=False, post_metadata_txt_pattern="", request_timeout=30.0)
        self.save_dir = save_dir
        self.record_file = save_dir + "/record.json"
        self.log_file = save_dir + "/log.txt"
        self.exit_flag = False
        self.init_flag = False
        try:
            if os.path.exists(self.record_file):
                with open(self.record_file, "r") as f:
                    self.record = json.load(f)
                self.username = self.record["username"] if "username" in self.record else ""
                self.password = self.record["password"] if "password" in self.record else ""
                self.interval = self.record["interval"] if "interval" in self.record else 15
                self.downloaded = self.record["downloaded"] if "downloaded" in self.record else [
                ]
                # if has wrong record
                if self.username == "" or self.password == "" or self.interval < 0:
                    self.log("wrong record")
                else:
                    self.session_file = save_dir + "/sessions/session-" + self.username
                    # successfully initial flag
                    self.init_flag = True
            else:
                # record file does not exist, create and write basic data
                with open(self.record_file, "w") as f:
                    default_record = {'username': '', 'password': '', 'interval': 15, 'downloaded': []}
                    json.dump(default_record, f, separators=(', ', ': '), indent=4)
                    self.log("edit record.json first")
        except Exception as e:
            self.log(f"initial fail, error: {e}")

    def login(self) -> bool:
        try:
            # if session file exists
            if os.path.exists(self.session_file):
                self.log("find session, try to load session...")
                self.loader.load_session_from_file(
                    self.username, self.session_file)
                self.log("load session successfully")
            # login with password and save session
            else:
                self.log("find no session, try to login with password...")
                self.loader.login(self.username, self.password)
                self.log("login successfully")
                try:
                    self.loader.save_session_to_file(self.session_file)
                    self.log("save session successfully")
                except Exception as e:
                    self.log(f"fail to save session, error: {e}")
            return True
        except Exception as e:
            self.log(f"login fail, error: {e}")
            return False
        except KeyboardInterrupt:
            ins.exit_flag = True

    def download(self):
        try:
            # get profile
            profile = instaloader.Profile.from_username(
                self.loader.context, self.username)
            # get saved posts
            posts = profile.get_saved_posts()
            # download saved posts
            os.chdir(self.save_dir)
            save_count = 0
            fail_count = 0
            self.log("start to download...")
            for post in posts:
                if post.shortcode not in self.downloaded:
                    if self.loader.download_post(post, "ins_saved"):
                        self.log(f"download success, shortcode: {post.shortcode}")
                        self.downloaded.append(post.shortcode)
                        save_count += 1

                        # this is for test
                        # if save_count == 2: break

                    else:
                        self.log(f"download fail, shortcode: {post.shortcode}")
                        fail_count += 1
            self.log(
                f"download completes, save count: {save_count}, fail count: {fail_count}")
        except Exception as e:
            self.log(f"error happen: {e}")
        except KeyboardInterrupt:
            self.exit_flag = True
        finally:
            # renew record
            self.record["downloaded"] = self.downloaded
            try:
                with open(self.record_file, "w") as f:
                    json.dump(self.record, f, separators=(', ', ': '), indent=4)
            except Exception as e:
                self.log(f"renew record fail, error: {e}")

    # print and log
    def log(self, msg):
        print(msg)
        with open(self.log_file, "a") as f:
            if msg == "":
                f.write("\n")
            else:
                f.write("********** " + time.strftime("%Y-%m-%d_%H-%M-%S_",
                        time.localtime(time.time())) + ": " + msg + "\n")


if __name__ == "__main__":
    # get the save directory
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", type=str, default=os.getcwd() +
                        "/ins", help="the directory to save files, should be absolute path")
    args = parser.parse_args()
    save_dir = args.dir
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # start to download
    ins = InsBatchAutoDownloader(save_dir)
    if ins.init_flag and ins.login():
        while True:
            ins.log("### DOWNLOAD PROCESS START ###")
            ins.download()
            ins.log("### DOWNLOAD PROCESS END ###")
            if ins.exit_flag:
                ins.log("exit successfully")
                break
            try:
                time.sleep(ins.interval * 60)
            except KeyboardInterrupt:
                ins.log("exit successfully")
                break
