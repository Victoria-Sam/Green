from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Event:
    event_type: int


@dataclass
class Map:
    idx: int
    lines: List[Line]
    name: str
    points: List[Point]


@dataclass
class Game:
    name: str
    num_players: int
    num_turns: int
    state: int


@dataclass
class Post:
    post_id: int
    events: List[Event]
    name: str
    point_id: int
    post_type: int


@dataclass
class Home:
    home_id: int
    post_id: int
    town: Town = None


@dataclass
class Line:
    idx: int
    length: int
    points: List[int]


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
class Point:
    idx: int
    post_id: int


@dataclass
class PointWithCoordinates:
    idx: int
    x: int
    y: int


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
class Rating:
    idx: str
    name: str
    rating: int


@dataclass
class Train:
    cooldown: int
    events: List[Event]
    fuel: int
    fuel_capacity: int
    fuel_consumption: int
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
    trains: List[Train]


@dataclass
class Map0Response(Response):
    graph_map: Map


@dataclass
class Map1Response(Response):
    idx: int
    posts: List[Post]
    ratings: Dict[str, Rating]
    trains: List[Train]


@dataclass
class Map10Response(Response):
    idx: int
    coordinates: List[PointWithCoordinates]
    size: List[int]


@dataclass
class GamesResponce(Response):
    games: List[Game]


p = GamesResponce(0, 25, [Game('qweqwr', 4, 100, 2), Game('boris', 5, 50, 1)])
print(p.games[1].name)
