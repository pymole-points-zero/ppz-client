from pydantic import BaseModel
from typing import List


class NextMatchGame(BaseModel):
    game_type: str
    match_game_id: int
    best_network_sha: str
    candidate_sha: str
    parameters: List
    field_width: int
    field_height: int
    candidate_turns_first: bool


class NextTrainingGame(BaseModel):
    game_type: str
    training_run_id: int
    network_id: int
    best_network_sha: str
    parameters: List
    field_width: int
    field_height: int
    keep_time: int


class RequestError(BaseModel):
    error: str

