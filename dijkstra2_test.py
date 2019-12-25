import unittest

from dijkstra import dijkstra, the_best_way
from classes_library import Line, Point, Graph


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.points = points = {
            0: Point(idx=0, post_id=0, point_type=1),
            1: Point(idx=1, post_id=0, point_type=3),
            2: Point(idx=2, post_id=0, point_type=None),
            3: Point(idx=3, post_id=0, point_type=2)
        }

        edges = {
            1: Line(idx=1, length=5, points=[points[0], points[1]]),
            2: Line(idx=2, length=10, points=[points[0], points[2]]),
            3: Line(idx=3, length=10, points=[points[2], points[3]]),
            4: Line(idx=4, length=5, points=[points[1], points[3]]),
        }
        self.graph = Graph(points, edges)

    def test_dijkstra1(self):
        result = dijkstra(self.graph, 0, 3)
        self.assertEqual(result[3][0].idx, 2)
        self.assertEqual(result[3][1].idx, 3)
        self.assertEqual(result[3][-1], 20)

    def test_dijkstra2(self):
        result = dijkstra(self.graph, 3, 3)
        self.assertEqual(result, {})

    def test_the_best_way(self):
        result = the_best_way(self.graph, 0)
        self.assertEqual(result[3][0].idx, 2)
        self.assertEqual(result[3][1].idx, 3)
        self.assertEqual(result[3][-1], 20)

    def test_the_best_way_2(self):
        result = the_best_way(self.graph, 3)
        self.assertEqual(result[0][0].idx, 4)
        self.assertEqual(result[0][1].idx, 1)
        self.assertEqual(result[0][-1], 10)


if __name__ == '__main__':
    unittest.main()
