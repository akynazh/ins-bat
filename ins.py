import instaloader
import json
import sys
import os
import time

# login and download record
record = {}
# the file that records a login session
session_file = ""
# get instaloader, no video thumnail, metadata and description
L = instaloader.Instaloader(download_video_thumbnails=False,
                            save_metadata=False, post_metadata_txt_pattern="")
login_user_name = ""
# path that saves information and files
root_path = ""

def load_record():
    global record, session_file, L, login_user_name, root_path
    record_path = root_path + "/record.json" 
    # if record does not exist, initial it
    if not os.path.exists(record_path):
        ins_log("record does not exist, initial record")
        with open(record_path, "w") as f:
            f.write('{"accounts": {},"downloaded": []}')
    with open(record_path, "r") as f:
        record = json.load(f)

def login():
    global record, session_file, L, login_user_name, root_path
    # get accounts
    accounts = record["accounts"]

    # if login before
    if login_user_name in accounts.keys():
        # if session_file still exists
        if os.path.exists(session_file):
            ins_log("login from session, username: " + login_user_name)
            L.load_session_from_file(login_user_name, session_file)
        # if session_file has been removed
        else:
            ins_log("session file not found, login with password, username: " + login_user_name)
            L.login(login_user_name, accounts[login_user_name])
    # new login
    else:
        password = input("new login, please input your password:")
        ins_log("new login, username: " + login_user_name)
        L.login(login_user_name, password)
        accounts[login_user_name] = password
        # renew accounts in record
        record["accounts"] = accounts
    ins_log("login success")

def download():
    global record, session_file, L, login_user_name, root_path
    profile = instaloader.Profile.from_username(L.context, login_user_name)
    # get saved posts
    posts = profile.get_saved_posts()
    # get downloaded posts first
    downloaded = record["downloaded"]
    # download saved posts
    os.chdir(root_path)
    save_count = 0
    for post in posts:
        if post.shortcode not in downloaded:
            # L.download_post(post, "ins_saved")
            downloaded.append(post.shortcode)
            save_count += 1

            # for test
            # if count == 2: break

    ins_log("download completes, save count: " + str(save_count) + ", pass count: " + str(posts.count - save_count))
    # renew downloaded in record
    record['downloaded'] = downloaded
    
def renew_record():
    global record, session_file, L, login_user_name, root_path
    # renew record
    with open(root_path + "/record.json", "w") as f:
        json.dump(record, f)

def ins_log(msg):
    print(msg)
    log_file = root_path + "/ins-log.txt"
    with open(log_file, "a") as f:
        f.write("********** " + time.strftime("%Y-%m-%d_%H-%M-%S_", time.localtime(time.time())) + ": " + msg + "**********\n")

# python ins.py {login_user_name} {root_path}
if __name__ == "__main__":
    try:
        login_user_name = sys.argv[1]
        if len(sys.argv) == 3:
            root_path = sys.argv[2]
        else:
            root_path = "ins" # default path
    except:
        print("command error: need argv")
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    session_file = root_path + "/sessions/session-" + login_user_name
    
    load_record()
    login()
    download()
    renew_record()

    L.save_session_to_file(session_file)