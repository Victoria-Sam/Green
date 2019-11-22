from server_connection import *
class Connection:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Connection, cls).__new__(cls)
            cls.sock = socket.socket()
            cls.sock.connect(('wgforge-srv.wargaming.net', 443))
        return cls.instance

    def login(self, name):
        return  message_to_server(self.sock, 'LOGIN', name=name)

    def map0(self):
        return JsonParser.json_to_graph(message_to_server(self.sock, 'MAP', layer=0))

    def map1(self):
        return JsonParser.json_to_posts_types(message_to_server(self.sock, 'MAP', layer=1))

    def move(self, line_idx, speed, train_idx):
        return message_to_server(self.sock, 'MOVE', line_idx=line_idx, speed=speed, train_idx=train_idx)

    def turn(self):
        message_to_server(self.sock, 'TURN')

c = Connection()
c.login('Sasha')
print(c.map0().edges(data=True))
print()
c.move(line_idx=1,speed=1,train_idx=1)
c.turn()
print()
    

