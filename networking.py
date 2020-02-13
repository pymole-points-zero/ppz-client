import requests
import config
from models import NextMatchGame, NextTrainingGame, RequestError
import pydantic


def next_game(username, password):
    params = {'username': username, 'password': password}

    try:
        response = requests.post(config.SERVER_URL + 'next_game', json=params)
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
        response = requests.get(config.SERVER_URL + 'download_network', json=params)
        with open(config.NETWORKS_FOLDER / sha, 'wb') as f:
            f.write(response.content)
    except:
        raise Exception