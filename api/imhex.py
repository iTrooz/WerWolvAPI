from flask import Blueprint, request, Response
import os
from pathlib import Path
import hashlib
import subprocess
import shutil
import threading

import config
from cache import cache

import hashlib
import hmac
import json
from datetime import date
import random
import tarfile

api_name = Path(__file__).stem
app = Blueprint(api_name, __name__, url_prefix = "/" + api_name)

app_data_folder = Path(config.Common.DATA_FOLDER) / api_name
app_content_folder = Path(config.Common.CONTENT_FOLDER) / api_name


store_folders = [ "patterns", "includes", "magic", "constants", "yara" ]
tips_folder = "tips"

def setup():
    os.system(f"git -C {app_data_folder} clone https://github.com/WerWolv/ImHex-Patterns --recurse-submodules")
    os.system(f"git -C {app_data_folder} clone https://github.com/file/file")

def init():
    pass

def update_git_repo(repo):
    repo_dir = app_data_folder / repo
    subprocess.call([ "git", "reset", "--hard" ], cwd = repo_dir)
    subprocess.call([ "git", "clean", "-fd" ], cwd = repo_dir)
    subprocess.call([ "git", "pull" ], cwd = repo_dir)

def update_data():
    try:
        print("Pulling changes...")
        update_git_repo("ImHex-Patterns")
        update_git_repo("file")
        
        """
        print("Building...")
        file_repo_dir = app_data_folder / "file"
        subprocess.call([ "autoreconf", "-f", "-i" ], cwd = file_repo_dir)
        subprocess.call([ "make", "distclean" ], cwd = file_repo_dir)
        subprocess.call([ "./configure", "--disable-silent-rules" ], cwd = file_repo_dir)
        subprocess.call([ "make", "-j" ], cwd = file_repo_dir)
        shutil.copyfile(app_data_folder / "file/magic/magic.mgc", app_data_folder / "ImHex-Patterns/magic/standard_magic.mgc")
        """
        shutil.rmtree(app_content_folder)
        os.makedirs(app_content_folder)

        print("Taring...")
        for store_folder in store_folders:
            store_path = app_data_folder / "ImHex-Patterns" / store_folder
            for entry in store_path.iterdir():
                if entry.is_dir():
                    shutil.make_archive(entry, "tar", entry)

        print("Copying...")
        for folder in store_folders:
            shutil.copytree(app_data_folder / "ImHex-Patterns" / folder, app_content_folder / folder)
    finally:
        cache.set("store_up_to_date", False)
        cache.set("updater_running", False)

@app.route("/pattern_hook", methods = [ 'POST' ])
def pattern_hook():
    signature = hmac.new(config.ImHexApi.SECRET, request.data, hashlib.sha1).hexdigest()

    if "X-Hub-Signature" not in request.headers:
        return Response(status = 401)


    if hmac.compare_digest(signature, request.headers['X-Hub-Signature'].split('=')[1]):
        print("Repository push detected!")

        if not cache.get("updater_running"):
            cache.set("updater_running", True)
            threading.Thread(target = update_data).start()
        else:
            print("Already updating. Skipped building again")

        return Response(status = 200)
    else:
        return Response(status = 401)

@app.route("/store")
def store():   
    update_data()
    if not cache.get("store_up_to_date"):
        store = {}
        for folder in store_folders:
            store[folder] = []
            for file in (app_data_folder/ "ImHex-Patterns" / folder).iterdir():
                if not file.is_dir():
                    with open(file, "rb") as fd:
                        store[folder].append({
                            "name": Path(file).stem.replace("_", " ").title(),
                            "desc": "",
                            "file": str(file),
                            "url": f"{request.root_url}/content/imhex/{folder}/{file}",
                            "hash": hashlib.sha256(fd.read()).hexdigest(),
                            "folder": Path(file).suffix == ".tar"
                            })

        cache.set("store_up_to_date", True)
        cache.set("store", store)

    return cache.get("store")

@app.route("/tip")
def get_tip():    
    current_day = date.today().weekday()

    if cache.get("tip_update_date") != current_day:
        cache.set("tip_update_date", current_day)

        files = [file for file in (app_data_folder / "ImHex-Patterns" / tips_folder).iterdir()]
        
        with open(random.choice(files)) as fd:
            json_data = json.load(fd)
            tips = json_data['tips']
            cache.set("tip", random.choice(tips))


    return cache.get("tip")