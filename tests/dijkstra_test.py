import unittest

from dijkstra import dijkstra, the_best_way
from classes_library import Line, Point, Graph


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.points = points = {
            0: Point(idx=0, post_id=0, point_type=1),
            1: Point(idx=1, post_id=0, point_type=None),
            2: Point(idx=2, post_id=0, point_type=2),
            3: Point(idx=3, post_id=0, point_type=2),
            4: Point(idx=4, post_id=0, point_type=None),
            5: Point(idx=5, post_id=0, point_type=None),
            6: Point(idx=6, post_id=0, point_type=None),
            7: Point(idx=7, post_id=0, point_type=3)
        }

        edges = {
            1: Line(idx=1, length=5, points=[points[0], points[1]]),
            2: Line(idx=2, length=8, points=[points[0], points[6]]),
            3: Line(idx=3, length=9, points=[points[0], points[4]]),
            4: Line(idx=4, length=15, points=[points[1], points[3]]),
            5: Line(idx=5, length=12, points=[points[1], points[2]]),
            6: Line(idx=6, length=4, points=[points[1], points[6]]),
            7: Line(idx=7, length=7, points=[points[6], points[2]]),
            8: Line(idx=8, length=6, points=[points[6], points[5]]),
            9: Line(idx=9, length=5, points=[points[4], points[6]]),
            10: Line(idx=10, length=4, points=[points[4], points[5]]),
            11: Line(idx=11, length=1, points=[points[5], points[2]]),
            12: Line(idx=12, length=3, points=[points[2], points[3]]),
            13: Line(idx=13, length=11, points=[points[2], points[7]]),
            14: Line(idx=14, length=9, points=[points[3], points[7]]),
            15: Line(idx=15, length=13, points=[points[5], points[7]]),
            16: Line(idx=16, length=20, points=[points[4], points[7]]),
        }
        self.graph = Graph(points, edges)

    def test_dijkstra1(self):
        result = dijkstra(self.graph, 0, 3)
        self.assertEqual(result[2][0].idx, 3)
        self.assertEqual(result[2][1].idx, 10)
        self.assertEqual(result[2][2].idx, 11)
        self.assertEqual(result[2][-1], 14)

    def test_dijkstra2(self):
        result = dijkstra(self.graph, 3)
        self.assertEqual(result[7][0].idx, 14)
        self.assertEqual(result[7][-1], 9)
        self.assertEqual(result[0][0].idx, 12)
        self.assertEqual(result[0][1].idx, 11)
        self.assertEqual(result[0][2].idx, 10)
        self.assertEqual(result[0][3].idx, 3)
        self.assertEqual(result[0][-1], 17)

    def test_the_best_way(self):
        result = the_best_way(self.graph, 0)
        self.assertEqual(result[2][0].idx, 3)
        self.assertEqual(result[2][1].idx, 10)
        self.assertEqual(result[2][2].idx, 11)
        self.assertEqual(result[2][-1], 14)


if __name__ == '__main__':
    unittest.main()
