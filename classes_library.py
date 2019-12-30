from dataclasses import dataclass
from typing import List, Dict


event_types = {
    "TRAIN_COLLISION": 1,
    "HIJACKERS_ASSAULT": 2,
    "PARASITES_ASSAULT": 3,
    "REFUGEES_ARRIVAL": 4,
    "RESOURCE_OVERFLOW": 5,
    "RESOURCE_LACK": 6,
    "GAME_OVER": 100
}


@dataclass
class Event:
    event_type: int
    tick: int


@dataclass
class TrainCollisionEvent(Event):
    second_train_id: int


@dataclass
class ParasitesAssaultEvent(Event):
    parasites_power: int


@dataclass
class HijackersAssaultEvent(Event):
    hijackers_power: int


@dataclass
class RefugeesArrivalEvent(Event):
    refugees_number: int


@dataclass
class ResourceOverflowEvent(Event):
    product: int = None
    armor: int = None


@dataclass
class ResourceLackEvent(Event):
    product: int = None
    armor: int = None


@dataclass
class GameOverEvent(Event):
    population: int = None


@dataclass
class Point:
    idx: int
    post_id: int
    point_type: int = None


@dataclass
class Line:
    idx: int
    length: int
    points: List[Point]


@dataclass
class Graph:
    points: Dict[int, Point]
    lines: Dict[int, Line]


def get_point(graph, idx):
    return graph.points[idx]


def get_line(graph, idx):
    return graph.lines[idx]


@dataclass
class Map:
    idx: int
    name: str
    graph: Graph


@dataclass
class Game:
    name: str
    num_players: int
    num_turns: int
    state: int


@dataclass
class Post:
    idx: int
    events: List[Event]
    name: str
    point_id: int
    post_type: int


@dataclass
class Town(Post):
    armor: int
    armor_capacity: int
    level: int
    next_level_price: int
    player_id: str
    population: int
    population_capacity: int
    product: int
    product_capacity: int
    train_cooldown: int


@dataclass
class Home:
    idx: int
    post_idx: int
    town: Town = None


@dataclass
class Market(Post):
    product: int
    product_capacity: int
    replenishment: int


@dataclass
class Storage(Post):
    armor: int
    armor_capacity: int
    replenishment: int


@dataclass
class PointWithCoordinates:
    idx: int
    x: int
    y: int


@dataclass
class Rating:
    idx: str
    name: str
    rating: int
    town_name: str


@dataclass
class Train:
    cooldown: int
    events: List[Event]
    # fuel: int
    # fuel_capacity: int
    # fuel_consumption: int
    goods: int
    goods_capacity: int
    goods_type: int
    train_id: int
    level: int
    line_id: int
    next_level_price: int
    player_id: str
    position: int
    speed: int


@dataclass
class Response:
    result_code: int
    response_length: int


@dataclass
class PlayerResponse(Response):
    home: Home
    player_id: str
    in_game: bool
    name: str
    rating: int
    town: Town
    trains: Dict[int, Train]


@dataclass
class Map0Response(Response):
    graph_map: Map


@dataclass
class Map1Response(Response):
    idx: int
    posts: Dict[int, Post]
    ratings: Dict[str, Rating]
    trains: Dict[int, Train]


@dataclass
class Map10Response(Response):
    idx: int
    coordinates: Dict[int, PointWithCoordinates]
    size: List[int]


@dataclass
class GamesResponce(Response):
    games: Dict[str, Game]


@dataclass
class UpgradeResponse(Response):
    error: str = None


@dataclass
class TurnResponse(Response):
    error: str = None


@dataclass
class MoveResponse(Response):
    error: str = None
