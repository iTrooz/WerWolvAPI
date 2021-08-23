from flask import Blueprint, request, Response, session
import os

from .. import config

import hashlib
import hmac
import json
from datetime import date
import random

api_name = os.path.splitext(os.path.basename(__file__))[0]
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

        session["contents_up_to_date"] = False

        return Response(status = 200)
    else:
        return Response(status = 401)

@app.route("/content")
def content():   
    if not session["contents_up_to_date"]:
        session["contents"]["patterns"] = []
        for file in os.listdir("./data/ImHex-Patterns/patterns"):
            session["contents"]["patterns"].append("https://raw.githubusercontent.com/WerWolv/ImHex-Patterns/master/patterns/" + file)

        session["contents"]["includes"] = []
        for file in os.listdir("./data/ImHex-Patterns/includes"):
            session["contents"]["includes"].append("https://raw.githubusercontent.com/WerWolv/ImHex-Patterns/master/includes/" + file)

        session["contents"]["magic"] = []
        for file in os.listdir("./data/ImHex-Patterns/magic"):
            session["contents"]["magic"].append("https://raw.githubusercontent.com/WerWolv/ImHex-Patterns/master/magic/" + file)



        session["contents_up_to_date"] = True

    return session["contents"]

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