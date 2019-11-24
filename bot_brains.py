import asyncio
from Connection import Connection


class BotBrains:

    def __init__(self, main_window, user_name):
        self.connection = Connection()
        self.main_window = main_window
        self.__coroutine = None
        self.user_name = user_name
        self.map0 = None
        self.map1 = None

    def start(self):
        self.__coroutine = asyncio.ensure_future(self.main_loop())

    @asyncio.coroutine
    def init_bot(self):
        yield from self.connection.login(self.user_name)
        yield from self.draw_map0()

    @asyncio.coroutine
    def main_loop(self):
        yield from self.init_bot()

        while True:
            yield from self.move_trains()
            yield from self.turn()
            yield from self.update_map1()

    def close_bot(self):
        self.__coroutine.cancel()

    async def move_trains(self):
        # пойми куда пойти
        print('move train')
        pass

    async def turn(self):
        # пока надо, чтобы видеть как будет двигаться поезд
        await asyncio.sleep(3)

        response = await self.connection.turn()
        print('turn end')

    async def draw_map0(self):
        self.map0 = await self.connection.map0()
        self.map1 = await self.connection.map1()

        edge_labels = {
            (edge[0], edge[1]):
                edge[2]['length'] for edge in list(self.map0.edges(data=True))
        }

        self.main_window.draw_map0(self.map0, edge_labels, self.map1)

    async def update_map1(self):
        self.map1 = await self.connection.map1()
        self.main_window.update_map1(self.map1)
