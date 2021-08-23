from os.path import dirname, basename, isfile, join
import secrets
import importlib
import glob

import config

from flask import Flask
app = Flask(__name__)

@app.route("/")
def base():
    return "WerWolv's API Endpoints"


app.secret_key = config.Common.SECRET

modules = glob.glob(join(dirname(__file__), "api/*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
for file in __all__:
    module = importlib.import_module("api." + file)
    app.register_blueprint(module.app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')