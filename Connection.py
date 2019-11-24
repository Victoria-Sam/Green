from server_connection import *
class Connection:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Connection, cls).__new__(cls)
            cls.sock = socket.socket()
            cls.sock.connect(('wgforge-srv.wargaming.net', 443))
        return cls.instance

    async def login(self, name):
        return await message_to_server(self.sock, 'LOGIN', name=name)

    async def map0(self):
        return JsonParser.json_to_graph(await message_to_server(self.sock, 'MAP', layer=0))

    async def map1(self):
        return JsonParser.json_to_posts_types(await message_to_server(self.sock, 'MAP', layer=1))

    async def move(self, line_idx, speed, train_idx):
        return await message_to_server(self.sock, 'MOVE', line_idx=line_idx, speed=speed, train_idx=train_idx)

    async def turn(self):
        return await message_to_server(self.sock, 'TURN')

    def close(self):
        self.sock.close()



#c = Connection()
#c.login('Sasha')
#print(c.map0().edges(data=True))
#print()
#c.move(line_idx=1,speed=1,train_idx=1)
#c.turn()
#print()
    

