import requests
import config
from models import NextMatchGame, NextTrainingGame, RequestError
import pydantic
import gzip


def next_game(username, password):
    params = {'username': username, 'password': password}

    try:
        response = requests.post(config.SERVER_URL + '/next_game', json=params)
        data = response.json()
    except ValueError:
        raise Exception

    try:
        error = RequestError(**data)
        raise Exception
    except pydantic.ValidationError as e:
        pass

    try:
        return NextTrainingGame(**data)
    except pydantic.ValidationError as e:
        pass

    try:
        return NextMatchGame(**data)
    except pydantic.ValidationError as e:
        pass

    raise Exception


def download_network(sha):
    params = {'sha': sha}

    try:
        response = requests.get(config.SERVER_URL + '/download_network', json=params)
        with open(config.NETWORKS_FOLDER / (sha + '.h5'), 'wb') as f:
            f.write(gzip.decompress(response.content))
    except:
        raise Exception


def upload_match_game(match_file_path, match_game_id, result):
    with open(match_file_path, 'r') as f:
        data = {
            'match_game_id': match_game_id,
            'result': result,
            'match_game_file': (None, f)
        }

    try:
        # да, это странновато, что чтобы послать multipart, нужно указать параметр files,
        # в котором как раз и будет словарь
        response = requests.post(config.SERVER_URL + '/upload_match_game', files=data)
    except:
        raise Exception


def upload_training_game(training_example_path, training_game_sgf_path, training_run_id, network_id):
    data = {
        'training_run_id': training_run_id,
        'network_id': network_id
    }

    with open(training_example_path, 'rb') as f:
        data['training_example'] = f

    with open(training_game_sgf_path, 'rb') as f:
        data['training_game_sgf'] = f

    try:
        response = requests.post(config.SERVER_URL + '/upload_training_game', files=data)
    except:
        raise Exception
