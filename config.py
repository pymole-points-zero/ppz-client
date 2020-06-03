from pathlib import Path
import os


BASE_PATH = Path.cwd()
CREDENTIALS_PATH = Path('credentials.json')
ENGINE_MAIN_PATH = BASE_PATH.parent / 'ppz-engine' / 'main.py'

if os.name == 'nt':
    VENV_PATH = BASE_PATH.parent / 'ppz-engine' / 'venv' / 'Scripts' / 'python'
elif os.name == 'posix':
    VENV_PATH = BASE_PATH.parent / 'ppz-engine' / 'venv' / 'bin' / 'python'
else:
    raise OSError

NETWORKS_FOLDER = BASE_PATH / 'networks'
SERVER_URL = 'http://192.168.0.7:8000'
