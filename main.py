import json
import sys

import networking
from config import CREDENTIALS_PATH
import options
import config
import subprocess


def create_credentials():
    username = input('Username: ')
    password = input('Password: ')

    with open(CREDENTIALS_PATH, 'w') as f:
        json.dump({'username': username, 'password': password}, f)

    return username, password


def yes_or_no(question):
    print(question)

    while True:
        answer = input()

        if answer == 'y':
            return True
        if answer == 'n':
            return False

        print('Input y or n: ', end='')


# получаем логин и пароль пользователя

# проверяем файл данных пользователя
if CREDENTIALS_PATH.exists():
    try:
        # пытаемся открыть файл
        with open(CREDENTIALS_PATH, 'r') as f:
            data = json.load(f)

        # пытаемся получить учетные данные из файла
        username = data['username']
        password = data['password']

    except (KeyError, json.JSONDecodeError):
        is_creating_new = yes_or_no(f"Corrupted credentials at: {CREDENTIALS_PATH}. Recreate credentials file?"
                                    "(you can input your old username and password or create new) y/n")

        if is_creating_new:
            username, password = create_credentials()
        else:
            sys.exit(0)
else:
    username, password = create_credentials()

if not config.NETWORKS_FOLDER.exists():
    config.NETWORKS_FOLDER.mkdir()


# главный цикл
while True:
    try:
        options.next_game = networking.next_game(username, password)
    except Exception:
        break

    print(options.next_game)

    # загружаем нейронные сети
    networking.download_network(options.next_game.best_network_sha)

    if options.next_game.game_type == 'match':
        networking.download_network(options.next_game.candidate_sha)

        process_args = [
            str(config.DEFAULT_ENGINE_PATH),
            'match',
            '--best_weights', str(config.NETWORKS_FOLDER / options.next_game.best_network_sha),
            '--candidate_weights', str(config.NETWORKS_FOLDER / options.next_game.candidate_sha),
            '--match_parameters', options.next_game.parameters,
        ]

        # ждем, пока отыграется матч
        engine_process = subprocess.Popen(process_args, shell=True, stdout=subprocess.PIPE)
        engine_process.wait()

    elif options.next_game.game_type == 'train':
        process_args = [
            str(config.DEFAULT_ENGINE_PATH),
            'selfplay',
            '--best_weights', str(config.NETWORKS_FOLDER / options.next_game.best_network_sha),
            '--training_parameters', options.next_game.parameters,
        ]

        # ждем, пока проведется игра нейронной сети с самой собой
        engine_process = subprocess.Popen(process_args, shell=True, stdout=subprocess.PIPE)
        engine_process.wait()

