import unittest
from dijkstra import the_best_way
from classes_library import Line, Point, Graph


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.points = points = [
            Point(idx=0, post_id=1),
            Point(idx=1, post_id=0),
            Point(idx=2, post_id=2),
            Point(idx=3, post_id=2),
            Point(idx=4, post_id=3),
            Point(idx=5, post_id=0),
            Point(idx=6, post_id=0)
        ]

        edges = [
            Line(idx=1, length=5, points=[points[0], points[1]]),
            Line(idx=2, length=8, points=[points[0], points[6]]),
            Line(idx=3, length=9, points=[points[0], points[4]]),
            Line(idx=4, length=15, points=[points[1], points[3]]),
            Line(idx=5, length=12, points=[points[1], points[2]]),
            Line(idx=6, length=4, points=[points[1], points[6]]),
            Line(idx=7, length=7, points=[points[6], points[2]]),
            Line(idx=8, length=6, points=[points[6], points[5]]),
            Line(idx=9, length=5, points=[points[4], points[6]]),
            Line(idx=10, length=4, points=[points[4], points[5]]),
            Line(idx=11, length=1, points=[points[5], points[2]]),
            Line(idx=12, length=3, points=[points[2], points[3]]),
        ]
        self.graph = Graph(points, edges)

    def test_dijkstra1(self):
        result = the_best_way(self.graph, Point(0, 1))
        self.assertEqual(result[2][0].idx, 3)
        self.assertEqual(result[2][1].idx, 10)
        self.assertEqual(result[2][2].idx, 11)
        self.assertEqual(result[2][-1], 14)

    def test_dijkstra2(self):
        result = the_best_way(self.graph, Point(3, 2))
        self.assertEqual(result[4][0].idx, 12)
        self.assertEqual(result[4][1].idx, 11)
        self.assertEqual(result[4][2].idx, 10)
        self.assertEqual(result[4][-1], 8)


if __name__ == '__main__':
    unittest.main()
