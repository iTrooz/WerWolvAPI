import os

class Common:
    SECRET = b''

class ImHexApi:
    SECRET = b''


def setup():
    os.system("git -C ./data/ImHex-Patterns clone https://github.com/WerWolv/ImHex-Patterns")
    pass

if __name__ == "__main__":
    setup()