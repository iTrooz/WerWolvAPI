from typing import Dict, List

import subprocess
import shutil
import hashlib
from pathlib import Path

import config


store_folders = [ "patterns", "includes", "magic", "constants", "yara", "encodings", "nodes", "themes" ]

def get_pattern_metadata(file_path: str, type_: str) -> str:
    """
    Get the associated metadata value of a pattern file, using the `plcli` tool. Returns None if the tool is not found

    type: metadata type to get. Valid values (as of 2023/08/21): name, authors, description, mime, version

    if any error occurs, returns an empty string
    """

    std_folder = Path(config.Common.CONTENT_FOLDER) / "imhex" / "includes"
    try:
        return subprocess.check_output(["plcli", "info", file_path, "-t", type_, "-I", std_folder]).decode()
    except subprocess.CalledProcessError as e:
        return ""

def is_plcli_found() -> bool:
    """
    Check if the plcli executable is found in the PATH
    """
    return shutil.which("plcli") is not None

def gen_store(root_url: str) -> Dict[str, List[Dict]]:
    """
    Generate an object representing the ImHex store, that can be returned by /imhex/store
    """
    plcli_found = is_plcli_found()
    store = {}
    for folder in store_folders:
        store[folder] = []
        for file in (Path(".") / "content" / "imhex" / folder).iterdir():
            if not file.is_dir():
                with open(file, "rb") as fd:
                    data = {
                        "name": Path(file).stem.replace("_", " ").title(),
                        "file": file.name,
                        "url": f"{root_url}content/imhex/{folder}/{file.name}",
                        "hash": hashlib.sha256(fd.read()).hexdigest(),
                        "folder": Path(file).suffix == ".tar",

                        "authors": [],
                        "desc": "",
                        "mime": "",
                        }
                    if folder == "patterns" and plcli_found:
                        data["authors"] = list(filter(None, get_pattern_metadata(file, "authors").split("\n")))
                        data["desc"] = get_pattern_metadata(file, "description")
                        data["mime"] = get_pattern_metadata(file, "mime")
                    store[folder].append(data)

    return store
