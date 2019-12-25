import unittest

from dijkstra import dijkstra, the_best_way
from classes_library import Line, Point, Graph


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.points = points = {
            0: Point(idx=0, post_id=0, point_type=1),
            1: Point(idx=1, post_id=0, point_type=None),
            2: Point(idx=2, post_id=0, point_type=2)
        }

        edges = {
            1: Line(idx=1, length=5, points=[points[0], points[1]])
        }
        self.graph = Graph(points, edges)

    def test_dijkstra1(self):
        result = dijkstra(self.graph, 2)
        self.assertEqual(result, {})

    def test_the_best_way(self):
        result = the_best_way(self.graph, 2)
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
