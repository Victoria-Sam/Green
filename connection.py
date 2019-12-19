from server_interaction_library import *


class Connection:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Connection, cls).__new__(cls)
            cls.sock = socket.socket()
            cls.sock.connect(('wgforge-srv.wargaming.net', 443))
        return cls.instance

    def login(self, name):
        return ResponseParser.response_to_player_response(
            message_to_server(self.sock, 'LOGIN', name=name))

    def map0(self):
        return ResponseParser.response_to_map0_response(
            message_to_server(self.sock, 'MAP', layer=0))

    def map1(self):
        return ResponseParser.response_to_map1_response(
           message_to_server(self.sock, 'MAP', layer=1))

    def move(self, line_idx, speed, train_idx):
        return ResponseParser.response_to_move_response(
            message_to_server(self.sock, 'MOVE', line_idx=line_idx,
                              speed=speed, train_idx=train_idx))

    def turn(self):
        return ResponseParser.response_to_turn_response(
            message_to_server(self.sock, 'TURN'))

    def upgrade(self, posts, trains):
        return ResponseParser.response_to_upgrade_response(
            message_to_server(self.sock, 'UPGRADE', posts=posts,
                              trains=trains))

    def close(self):
        self.sock.close()
