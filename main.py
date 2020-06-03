import json
import sys
import networking
from config import CREDENTIALS_PATH
import options
import config
import subprocess
import time
import argparse


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


# TODO временная мера, чтобы менять адрес сервера
parser = argparse.ArgumentParser()
parser.add_argument('--server', type=str, help='Server address', required=False)

args = parser.parse_args()

if args.server is not None:
    config.SERVER_URL = args.server
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

# TODO silent shutdown ctrl + C
# main loop
while True:
    try:
        options.next_game = networking.next_game(username, password)
    except Exception as e:
        print(e)
        break

    print(options.next_game)

    # TODO keep network for a while (caching)
    # download neural networks
    networking.download_network(options.next_game.best_network_sha)
    if options.next_game.game_type == 'match':
        networking.download_network(options.next_game.candidate_sha)
        command_args = [
            str(config.VENV_PATH),
            str(config.ENGINE_MAIN_PATH),
            'match',
            '--field_width', str(options.next_game.field_width),
            '--field_height', str(options.next_game.field_height),
        ] + options.next_game.parameters + [
            '--best_weights', str(config.NETWORKS_FOLDER / (options.next_game.best_network_sha + '.h5')),
            '--candidate_weights', str(config.NETWORKS_FOLDER / (options.next_game.candidate_sha + '.h5')),
        ]

        if options.next_game.candidate_turns_first:
            command_args.append('--candidate_turns_first')

        command_line = ' '.join(command_args)

        # ждем, пока отыграется матч
        start_time = time.time()
        engine_process = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE)
        output, err = engine_process.communicate()
        output = output.decode('utf-8')

        print(output)
        # TODO error handling when engine fails
        # получаем путь к файлу матча и результат
        match_file_path, result = output.split()

        print('Match ended in', time.time() - start_time)

        # отправляем результат отыгранного матча
        networking.upload_match_game(username, password, match_file_path, options.next_game.match_game_id, int(result))

    elif options.next_game.game_type == 'train':
        command_args = [
            str(config.VENV_PATH),
            str(config.ENGINE_MAIN_PATH),
            'selfplay',
            '--field_width', str(options.next_game.field_width),
            '--field_height', str(options.next_game.field_height),
        ] + options.next_game.parameters + [
            '--weights', str(config.NETWORKS_FOLDER / (options.next_game.best_network_sha + '.h5')),
        ]
        command_line = ' '.join(command_args)
        print(command_line)

        start_time = time.time()

        # ждем, пока проведется игра нейронной сети с самой собой
        engine_process = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE)
        output, err = engine_process.communicate()
        output = output.decode('utf-8')
        print(output)

        print('Selfplay ended in', time.time() - start_time)

        # TODO error handling when engine fails
        training_game_sgf_path, training_example_path = output.split()

        networking.upload_training_game(username, password, training_game_sgf_path, training_example_path,
                                        options.next_game.training_run_id, options.next_game.network_id)
