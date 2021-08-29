from flask import Blueprint, request, Response, session
import os
from pathlib import Path
import hashlib

import config

import hashlib
import hmac
import json
from datetime import date
import random

api_name = Path(__file__).stem
app = Blueprint(api_name, __name__, url_prefix = "/" + api_name)

@app.route("/")
def base():
    return "ImHex API Endpoint"

@app.route("/pattern_hook", methods = [ 'POST' ])
def pattern_hook():
    signature = hmac.new(config.ImHexApi.SECRET, request.data, hashlib.sha1).hexdigest()

    if hmac.compare_digest(signature, request.headers['X-Hub-Signature'].split('=')[1]):
        print("ImHex-Patterns Repo Push detected, pulling changes...")
        os.system("git -C ./data/ImHex-Patterns reset --hard")
        os.system("git -C ./data/ImHex-Patterns clean -fd")
        os.system("git -C ./data/ImHex-Patterns pull")

        session["store_up_to_date"] = False

        return Response(status = 200)
    else:
        return Response(status = 401)

@app.route("/store")
def store():   
    if "store_up_to_date" not in session:
        session["store_up_to_date"] = False

    if not session["store_up_to_date"]:
        session["store"] = { }

        for folder in [ "patterns", "includes", "magic" ]:
            session["store"][folder] = []
            for file in os.listdir(Path("./data/ImHex-Patterns") / folder):
                with open(Path("./data/ImHex-Patterns") /folder / file, "rb") as fd:
                    session["store"][folder].append({
                        "file": "https://raw.githubusercontent.com/WerWolv/ImHex-Patterns/master" + "/" + folder + "/" + file,
                        "hash": hashlib.sha256(fd.read()).hexdigest()
                        })

        session["store_up_to_date"] = True

    return session["store"]

@app.route("/tip")
def get_tip():    
    current_day = date.today().weekday()

    if not "tip_update_date" in session:
        session["tip_update_date"] = -1

    if session["tip_update_date"] != current_day:
        session["tip_update_date"] = current_day

        files = os.listdir("./data/ImHex-Patterns/tips")
        file = "./data/ImHex-Patterns/tips/" + random.choice(files)
        
        with open(file) as fd:
            json_data = json.load(fd)
            tips = json_data['tips']
            session["tip"] = random.choice(tips)


    return session["tip"]