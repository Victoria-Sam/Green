import unittest
import sys
sys.path.extend([".."])

from dijkstra import dijkstra, the_best_way
from classes_library import Line, Point, Graph, Train


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.all_trains = {
            1: Train(cooldown=1, events=[], goods=0, goods_capacity=40, goods_type=None, train_id=1, level=1, line_id=1,
                     next_level_price=40, player_id='ff4b8b11-8eb7-4c9c-b096-04758349ae52', position=5, speed=0)
        }

        self.points = points = {
            0: Point(idx=0, post_id=0, point_type=1),
            1: Point(idx=1, post_id=0, point_type=None),
            2: Point(idx=2, post_id=0, point_type=2)
        }

        edges = {
            1: Line(idx=1, length=5, points=[points[0], points[1]])
        }
        self.graph = Graph(points, edges)

    def test_dijkstra(self):
        result = dijkstra(self.graph, 2, 1, self.all_trains)
        self.assertEqual(result, {})

    def test_the_best_way(self):
        result = the_best_way(self.graph, 2, 1, self.all_trains)
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
