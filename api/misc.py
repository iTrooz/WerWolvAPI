from flask import Blueprint, request, Response
from pathlib import Path

import config
from cache import cache

api_name = Path(__file__).stem
app = Blueprint(api_name, __name__, url_prefix = "/" + api_name)

app_data_folder = Path(config.Common.DATA_FOLDER) / api_name
app_content_folder = Path(config.Common.CONTENT_FOLDER) / api_name

def setup():
    pass

def init():
    pass

@app.route("/teapot", methods = [ "GET" ])
def teapot():
    return Response(status = 418)