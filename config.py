from pathlib import Path

BASE_PATH = Path.cwd()
CREDENTIALS_PATH = Path('credentials.json')
ENGINE_MAIN_PATH = BASE_PATH.parent / 'ppz-engine' / 'main.py'
VENV_PATH = BASE_PATH.parent / 'ppz-engine' / 'venv' / 'bin' / 'python'
NETWORKS_FOLDER = BASE_PATH / 'networks'
SERVER_URL = 'http://127.0.0.1:8000'
