import itertools
from heapq import heappop, heappush


class PriorityQueue:

    def __init__(self):
        self.pq = []                        # list of entries arranged in a
        self.entry_finder = {}              # heap mapping of points to entries
        self.REMOVED = '<removed-point>'    # placeholder for a removed point
        self.counter = itertools.count()    # unique sequence count

    def add_point(self, point, priority):
        """Add a new task or update the priority of an existing task"""
        if point in self.entry_finder:
            self.remove_point(point)
        count = next(self.counter)
        entry = [priority, count, point]
        self.entry_finder[point] = entry
        heappush(self.pq, entry)

    def remove_point(self, point):
        """Mark an existing task as REMOVED.  Raise KeyError if not found."""
        entry = self.entry_finder.pop(point)
        entry[-1] = self.REMOVED

    def pop_point(self):
        """
        Remove and return the lowest priority point. Raise KeyError if empty.
        """
        while self.pq:
            priority, count, point = heappop(self.pq)
            if point is not self.REMOVED:
                del self.entry_finder[point]
                return point
        raise KeyError('pop from an empty priority queue')


def dijkstra(graph, start_point, forbidden_type=0):  # index os start point in dictionary graph.points
    dict_of_dist = {key: float('inf') for (key, value) in graph.points.items()}
    dict_of_edge_to = {key: None for (key, value) in graph.points.items()}
    dict_of_marks = {key: False for (key, value) in graph.points.items()}
    adjacency_list = {key: [] for (key, value) in graph.points.items()}
    priority = PriorityQueue()

    for index_of_point in graph.points.keys():
        priority.add_point(index_of_point, float('inf'))

    for line in graph.lines.values():  # creating of adjacency_list, format: {point_idx:[Line1, Line2]}
        index_a = line.points[0].idx
        adjacency_list[index_a].append(line)
        index_b = line.points[1].idx
        adjacency_list[index_b].append(line)

    index_of_start = start_point
    priority.add_point(index_of_start, 0)
    dict_of_dist[index_of_start] = 0

    while False in dict_of_marks.values():  # dijkstra
        index_of_start = priority.pop_point()
        dict_of_marks[index_of_start] = True
        start = index_of_start
        if graph.points[start].point_type == forbidden_type:
            continue
        for edge in adjacency_list[index_of_start]:
            index_of_neighbour = edge.points[0 if edge.points[1].idx == start else 1].idx
            new_path_length = edge.length + dict_of_dist[index_of_start]
            if new_path_length < dict_of_dist[index_of_neighbour]:
                dict_of_edge_to[index_of_neighbour] = edge
                dict_of_dist[index_of_neighbour] = new_path_length
                priority.add_point(index_of_neighbour, new_path_length)

    dict_of_shortest_ways = {}  # result
    post_type = [1, 2, 3]
    if forbidden_type != 0:  # type exclusion
        post_type.remove(forbidden_type)
        post_type.remove(1)

    for point_idx, point in graph.points.items():  # creating of result
        if point_idx != start_point and point.point_type in post_type:
            # if there is no path.
            if dict_of_edge_to[point_idx] is None:
                continue
            end_point = point_idx
            distance = dict_of_dist[end_point]
            shortest_way = []

            while end_point != start_point:
                part_of_the_way = dict_of_edge_to[end_point]
                shortest_way.append(part_of_the_way)
                intermediate_point = part_of_the_way.points[
                    0 if part_of_the_way.points[1].idx == end_point else 1].idx
                end_point = intermediate_point
            shortest_way = shortest_way[::-1]
            shortest_way.append(distance)
            dict_of_shortest_ways[point_idx] = shortest_way

    return dict_of_shortest_ways


def the_best_way(graph, start_point):
    """Builder, which make all shortest ways for destinations."""
    for_market = dijkstra(graph, start_point, 3)
    for_storage = dijkstra(graph, start_point, 2)
    home = dijkstra(graph, start_point)
    ways = {}
    ways.update(home)
    ways.update(for_market)
    ways.update(for_storage)
    return ways
