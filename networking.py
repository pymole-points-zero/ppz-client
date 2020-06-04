import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import config
from models import NextMatchGame, NextTrainingGame, RequestError
import pydantic
import gzip


retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["GET", "POST"],
    backoff_factor=10
)

adapter = HTTPAdapter(max_retries=retry_strategy)


# TODO сделать так, чтобы не приходилось каждый раз писать обработку ошибки со стороны сервера

def prepare_session():
    s = requests.Session()
    s.mount("https://", adapter)
    s.mount("http://", adapter)

    return s


def next_game(username, password):
    session = prepare_session()
    params = {'username': username, 'password': password}

    try:
        response = session.post(config.SERVER_URL + '/next_game', json=params)
        data = response.json()
    except ValueError:
        raise Exception

    try:
        error = RequestError(**data)
        raise Exception(error.error)
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
    session = prepare_session()
    # check if cached
    network_path = config.NETWORKS_FOLDER / (sha + '.h5')
    if network_path.exists():
        print(sha, 'is cached up')
        return

    params = {'sha': sha}

    try:
        response = session.get(config.SERVER_URL + '/download_network', json=params)
        with open(network_path, 'wb') as f:
            f.write(gzip.decompress(response.content))
    except:
        raise Exception


def upload_match_game(username, password, match_file_path, match_game_id, result):
    session = prepare_session()
    data = {
        'match_game_id': match_game_id,
        'result': result,
        'username': username,
        'password': password
    }

    sgf_file = open(match_file_path, 'r')

    files = {'match_game_sgf': sgf_file}

    try:
        response = session.post(config.SERVER_URL + '/upload_match_game', data=data, files=files)
    except:
        raise Exception
    finally:
        sgf_file.close()


def upload_training_game(username, password, training_game_sgf_path, training_example_path,
                         training_run_id, network_id):
    session = prepare_session()
    data = {
        'training_run_id': training_run_id,
        'network_id': network_id,
        'username': username,
        'password': password
    }

    sgf_file = open(training_game_sgf_path, 'r')
    example_file = open(training_example_path, 'rb')

    files = {
        'training_game_sgf': sgf_file,
        'training_example': example_file
    }

    try:
        response = requests.post(config.SERVER_URL + '/upload_training_game', data=data, files=files)
        data = response.json()
    except:
        raise Exception
    finally:
        sgf_file.close()
        example_file.close()

    try:
        error = RequestError(**data)
        raise Exception(error.error)
    except pydantic.ValidationError as e:
        pass
