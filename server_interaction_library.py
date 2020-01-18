import socket
import json

from classes_library import *
from typing import List, Dict

action_types = {'LOGIN': 1, 'LOGOUT': 2, 'MOVE': 3, 'UPGRADE': 4, 'TURN': 5,
                'PLAYER': 6, 'GAMES': 7, 'MAP': 10}
post_types = {1: 'town', 2: 'market', 3: 'storage'}

event_classes = {
    1: TrainCollisionEvent,
    2: HijackersAssaultEvent,
    3: ParasitesAssaultEvent,
    4: RefugeesArrivalEvent,
    5: ResourceOverflowEvent,
    6: ResourceLackEvent,
    100: GameOverEvent
}


def print_server_message(result):
    print("Result code:", result["result_code"])
    print("Response length:", result["response_length"])
    print("Response:\n", result["response"])


class ResponseParser:
    @staticmethod
    def response_to_map0_response(result) -> Map0Response:
        '''
        Convert json representation of Map 0 response into
        custom class Map0Response
        '''
        if result["result_code"] == 0:
            resp = result["response"]
            temp_points = {}
            for point in resp["points"]:
                temp_points[point["idx"]] = Point(point["idx"],
                                                  point["post_idx"])
            temp_lines = {}
            for line in resp["lines"]:
                temp_vertexes = [temp_points[line["points"][0]],
                                 temp_points[line["points"][1]]]
                temp_lines[line["idx"]] = Line(line["idx"], line["length"],
                                               temp_vertexes)
            temp_graph = Graph(temp_points, temp_lines)
            temp_map = Map(resp["idx"], resp["name"], temp_graph)
            return Map0Response(result["result_code"],
                                result["response_length"], temp_map)

    @staticmethod
    def response_to_map1_response(result) -> Map1Response:
        '''
        Convert json representation of Map 1 response into
        custom class Map1Response
        '''
        if result["result_code"] == 0:
            resp = result["response"]
            temp_posts_types = {}
            all_posts = resp["posts"]  # list of post dicts
            all_ratings = resp["ratings"]
            all_trains = resp["trains"]

            posts = {}
            ratings = {}
            trains = {}

            for post in all_posts:  # post = 1 dict from list
                events = list()
                all_events = post["events"]
                for event in all_events:
                    for key, value in event.items():
                        if key == "type":
                            temp_type = value
                        elif key == "tick":
                            temp_tick = value
                        else:
                            temp_event_param = value
                            if key == "product":
                                type_5_6_product = True
                                type_5_6_armor = False
                            elif key == "armor":
                                type_5_6_product = False
                                type_5_6_armor = True
                    if temp_type == 6 or temp_type == 5:
                        if type_5_6_product is True:
                            temp_event = event_classes[event["type"]](
                                temp_type, temp_tick, temp_event_param, None
                            )
                        else:
                            temp_event = event_classes[event["type"]](
                                temp_type, temp_tick, None, temp_event_param
                            )
                    else:
                        temp_event = event_classes[event["type"]](
                            temp_type, temp_tick, temp_event_param
                            )
                    events.append(temp_event)
                if post["type"] == 1:
                    temp_posts_types[post["point_idx"]] = 1
                    temp_town = Town(
                        post["idx"],
                        events,
                        post["name"],
                        post["point_idx"],
                        post["type"],
                        post["armor"],
                        post["armor_capacity"],
                        post["level"],
                        post["next_level_price"],
                        post["player_idx"],
                        post["population"],
                        post["population_capacity"],
                        post["product"],
                        post["product_capacity"],
                        post["train_cooldown"]
                    )
                    posts[post["point_idx"]] = temp_town
                elif post["type"] == 2:
                    temp_posts_types[post["point_idx"]] = 2
                    temp_market = Market(
                        post["idx"],
                        events,
                        post["name"],
                        post["point_idx"],
                        post["type"],
                        post["product"],
                        post["product_capacity"],
                        post["replenishment"]
                    )
                    posts[post["point_idx"]] = temp_market
                elif post["type"] == 3:
                    temp_posts_types[post["point_idx"]] = 3
                    temp_storage = Storage(
                        post["idx"],
                        events,
                        post["name"],
                        post["point_idx"],
                        post["type"],
                        post["armor"],
                        post["armor_capacity"],
                        post["replenishment"]
                    )
                    posts[post["point_idx"]] = temp_storage

            for rating in all_ratings.values():
                ratings[rating["idx"]] = Rating(rating["idx"],
                                                rating["name"],
                                                rating["rating"],
                                                rating["town"])

            for train in all_trains:
                temp_events = list()
                for event in train["events"]:
                    temp_events.append(
                        TrainCollisionEvent(1, event["tick"], event["train"]))
                temp_train = Train(
                        train["cooldown"],
                        temp_events,
                        train["goods"],
                        train["goods_capacity"],
                        train["goods_type"],
                        train["idx"],
                        train["level"],
                        train["line_idx"],
                        train["next_level_price"],
                        train["player_idx"],
                        train["position"],
                        train["speed"]
                )
                trains[train["idx"]] = temp_train
            return Map1Response(result["result_code"],
                                result["response_length"],
                                resp["idx"],
                                posts,
                                ratings,
                                trains),\
                temp_posts_types

    @staticmethod
    def response_to_map10_response(result) -> Map10Response:
        resp = result["response"]
        coords = resp["coordinates"]
        result_coords = {}
        x_size = resp["size"][0]
        y_size = resp["size"][1]
        for point in coords:
            result_coords[point["idx"]] = [float(point["x"])/x_size,
                                           float(point["y"])/y_size]
        return Map10Response(result["result_code"],
                             result["response_length"],
                             resp["idx"],
                             result_coords,
                             resp["size"]
                             )

    @staticmethod
    def response_to_player_response(result) -> PlayerResponse:
        '''
        Convert json representation of Player(or Login) response into
        custom class PlayerResponse
        '''
        if result["result_code"] == 0:
            resp = result["response"]

            town_info = resp["town"]
            events = list()
            all_events = town_info["events"]
            for event in all_events:
                for key, value in event.items():
                    if key == "type":
                        temp_type = value
                    elif key == "tick":
                        temp_tick = value
                    else:
                        temp_event_param = value
                temp_event = event_classes[event["type"]](
                    temp_type, temp_tick, temp_event_param
                    )
                events.append(temp_event)
            temp_town = Town(
                        town_info["idx"],
                        events,
                        town_info["name"],
                        town_info["point_idx"],
                        town_info["type"],
                        town_info["armor"],
                        town_info["armor_capacity"],
                        town_info["level"],
                        town_info["next_level_price"],
                        town_info["player_idx"],
                        town_info["population"],
                        town_info["population_capacity"],
                        town_info["product"],
                        town_info["product_capacity"],
                        town_info["train_cooldown"]
            )

            temp_home = Home(
                resp["home"]["idx"], resp["home"]["post_idx"], temp_town
            )

            trains = {}
            for train in resp["trains"]:
                temp_events = list()
                for event in train["events"]:
                    temp_events.append(
                        TrainCollisionEvent(1, event["tick"], event["train"]))
                temp_train = Train(
                        train["cooldown"],
                        temp_events,
                        train["goods"],
                        train["goods_capacity"],
                        train["goods_type"],
                        train["idx"],
                        train["level"],
                        train["line_idx"],
                        train["next_level_price"],
                        train["player_idx"],
                        train["position"],
                        train["speed"]
                )
                trains[train["idx"]] = temp_train

            player_response = PlayerResponse(
                result["result_code"],
                result["response_length"],
                temp_home,
                resp["idx"],
                resp["in_game"],
                resp["name"],
                resp["rating"],
                temp_town,
                trains
            )
            return player_response
        else:
            return PlayerResponse(result["result_code"],
                                  result["response_length"],
                                  None,
                                  None,
                                  None,
                                  None,
                                  None,
                                  None,
                                  None,
                                  result["response"])

    @staticmethod
    def response_to_logout_response(result) -> LogoutResponse:
        if result["result_code"] == 0:
            return LogoutResponse(0, 0)
        else:
            return LogoutResponse(result["result_code"],
                                  result["response_length"],
                                  result["response"])

    @staticmethod
    def response_to_upgrade_response(result) -> UpgradeResponse:
        if result["result_code"] == 0:
            return UpgradeResponse(0, 0)
        else:
            return UpgradeResponse(result["result_code"],
                                   result["response_length"],
                                   result["response"])

    @staticmethod
    def response_to_turn_response(result) -> TurnResponse:
        if result["result_code"] == 0:
            return TurnResponse(0, 0)
        else:
            return TurnResponse(result["result_code"],
                                result["response_length"],
                                result["response"])

    @staticmethod
    def response_to_move_response(result) -> MoveResponse:
        if result["result_code"] == 0:
            return MoveResponse(0, 0)
        else:
            return MoveResponse(result["result_code"],
                                result["response_length"],
                                result["response"])

    @staticmethod
    def response_to_games_response(result) -> GamesResponse:
        resp = result["response"]
        games = {}

        for game in resp["games"]:
            games[game["name"]] = Game(game["name"],
                                       game["num_players"],
                                       game["num_turns"],
                                       game["state"])

        return GamesResponse(result["result_code"],
                             result["response_length"],
                             games)


def message_to_server(sock, action, json_mode=True, **kwargs):
    '''
    Send message to the server and return result as dict with
    result code, response length and [json response message as dict] fields
    '''
    message_code = action_types[action]
    action_message = bytearray()
    action_message += message_code.to_bytes(4, byteorder='little')

    if kwargs:
        json_msg = json.dumps(kwargs)
        action_message += len(json_msg).to_bytes(4, byteorder='little')
        action_message.extend(json_msg.encode())
    else:
        action_message += len(kwargs).to_bytes(4, byteorder='little')
    sock.send(action_message)

    result_code = int.from_bytes(sock.recv(4), byteorder='little')
    response_length = int.from_bytes(sock.recv(4), byteorder='little')
    response = sock.recv(response_length, socket.MSG_WAITALL)
    return {"result_code": result_code,
            "response_length": response_length,
            "response": json.loads(response) if response and json_mode else
            response if response else None
            }
