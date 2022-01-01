from flask import Blueprint, request, Response
from pathlib import Path

import config
from cache import cache

import datetime
from dateutil.relativedelta import relativedelta

api_name = Path(__file__).stem
app = Blueprint(api_name, __name__, url_prefix = "/" + api_name)

app_data_folder = Path(config.Common.DATA_FOLDER) / api_name
app_content_folder = Path(config.Common.CONTENT_FOLDER) / api_name

def setup():
    pass

def init():
    pass

@app.route("/age", methods = [ "GET" ])
def age():
    return str(relativedelta(datetime.datetime.now(), datetime.datetime(1998, 11, 4, 0, 0, 0)).years)