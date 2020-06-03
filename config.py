from pathlib import Path
import os


BASE_PATH = Path.cwd()
CREDENTIALS_PATH = Path('credentials.json')
ENGINE_MAIN_PATH = BASE_PATH.parent / 'ppz-engine' / 'main.py'

# check if virtual environment exists
# if not then try to run global interpreter
VENV_PATH = BASE_PATH.parent / 'ppz-engine' / 'venv'

if VENV_PATH.exists():
    if os.name == 'nt':
        VENV_PATH = VENV_PATH / 'Scripts' / 'python'
    elif os.name == 'posix':
        VENV_PATH = VENV_PATH / 'bin' / 'python'
    else:
        raise OSError
else:
    VENV_PATH = 'python3'

NETWORKS_FOLDER = BASE_PATH / 'networks'
SERVER_URL = 'http://192.168.0.7:8000'
