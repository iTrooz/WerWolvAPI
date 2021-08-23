from pathlib import Path
import importlib

import config

from flask import Flask
app = Flask(__name__)

@app.route("/")
def base():
    return "WerWolv's API Endpoints"


app.secret_key = config.Common.SECRET

modules = (Path(__file__).parent / "api").glob("*.py")
__all__ = [ f.stem for f in modules if f.is_file() and f.name != '__init__.py']
for file in __all__:
    module = importlib.import_module("api." + file)
    app.register_blueprint(module.app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')