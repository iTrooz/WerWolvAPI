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

api_name = Path(__file__).stem
app = Blueprint(api_name, __name__, url_prefix = "/" + api_name)


def update_git_repo(repo):
    repo_dir = f"./data/{repo}"
    subprocess.call([ "git", "reset", "--hard" ], cwd = repo_dir)
    subprocess.call([ "git", "clean", "-fd" ], cwd = repo_dir)
    subprocess.call([ "git", "pull" ], cwd = repo_dir)

def update_data():
    print("Repo update detected, pulling changes...")
    update_git_repo("ImHex-Patterns")
    update_git_repo("file")
    
    print("Building...")
    
    file_repo_dir = "./data/file"
    subprocess.call([ "autoreconf", "-f", "-i" ], cwd = file_repo_dir)
    subprocess.call([ "make", "distclean" ], cwd = file_repo_dir)
    subprocess.call([ "./configure", "--disable-silent-rules" ], cwd = file_repo_dir)
    subprocess.call([ "make", "-j" ], cwd = file_repo_dir)
    shutil.copyfile("./data/file/magic/magic.mgc", "./data/ImHex-Patterns/magic/standard_magic.mgc")
    
    cache.set("store_up_to_date", False)
    cache.set("updater_running", False)

@app.route("/pattern_hook", methods = [ 'POST' ])
def pattern_hook():
    signature = hmac.new(config.ImHexApi.SECRET, request.data, hashlib.sha1).hexdigest()

    if "X-Hub-Signature" not in request.headers:
        return Response(status = 401)


    if hmac.compare_digest(signature, request.headers['X-Hub-Signature'].split('=')[1]):

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

    if not cache.get("store_up_to_date"):
        store = {}
        for folder in [ "patterns", "includes", "magic" ]:
            store[folder] = []
            for file in os.listdir(Path("./data/ImHex-Patterns") / folder):
                with open(Path("./data/ImHex-Patterns") / folder / file, "rb") as fd:
                    store[folder].append({
                        "name": Path(file).stem.replace("_", " ").title(),
                        "desc": "",
                        "file": file,
                        "url": "https://raw.githubusercontent.com/WerWolv/ImHex-Patterns/master" + "/" + folder + "/" + file,
                        "hash": hashlib.sha256(fd.read()).hexdigest()
                        })

        cache.set("store_up_to_date", True)
        cache.set("store", store)

    return cache.get("store")

@app.route("/tip")
def get_tip():    
    current_day = date.today().weekday()

    if cache.get("tip_update_date") != current_day:
        cache.set("tip_update_date", current_day)

        files = os.listdir("./data/ImHex-Patterns/tips")
        file = "./data/ImHex-Patterns/tips/" + random.choice(files)
        
        with open(file) as fd:
            json_data = json.load(fd)
            tips = json_data['tips']
            cache.set("tip", random.choice(tips))


    return cache.get("tip")