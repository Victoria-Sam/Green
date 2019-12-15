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


def the_best_way(graph, start_point):
    list_of_dist = [float('inf')] * len(graph.points)
    list_of_edge_to = [None] * len(graph.points)
    list_of_marks = [False] * len(graph.points)
    adjacency_list = []
    priority = PriorityQueue()

    for index_of_point, point in enumerate(graph.points):
        priority.add_point(index_of_point, float('inf'))
        adjacency_list.append([])

    for line in graph.lines:
        index_a = graph.points.index(line.points[0])
        adjacency_list[index_a].append(line)
        index_b = graph.points.index(line.points[1])
        adjacency_list[index_b].append(line)
    index_of_start = graph.points.index(start_point)
    priority.add_point(index_of_start, 0)
    list_of_dist[index_of_start] = 0

    while False in list_of_marks:
        index_of_start = priority.pop_point()
        list_of_marks[index_of_start] = True
        for edge in adjacency_list[index_of_start]:
            start = graph.points[index_of_start]
            index_of_neighbour = graph.points.index(
                edge.points[0 if edge.points[1] == start else 1])
            new_path_length = edge.length + list_of_dist[index_of_start]
            if new_path_length < list_of_dist[index_of_neighbour]:
                list_of_edge_to[index_of_neighbour] = edge
                list_of_dist[index_of_neighbour] = new_path_length
                priority.add_point(index_of_neighbour, new_path_length)

    dict_of_shortest_ways = {}
    post_type = [1, 2, 3]
    for point in graph.points:
        if point != start_point and point.post_id in post_type:
            end_point = point
            idx_dist = graph.points.index(point)
            distance = list_of_dist[idx_dist]
            shortest_way = []
            while end_point != start_point:
                idx_end_point = graph.points.index(end_point)
                part_of_the_way = list_of_edge_to[idx_end_point]
                shortest_way.append(part_of_the_way)
                intermediate_point = part_of_the_way.points[
                    0 if part_of_the_way.points[1] == end_point else 1]
                end_point = intermediate_point
            shortest_way = shortest_way[::-1]
            shortest_way.append(distance)
            dict_of_shortest_ways[point.idx] = shortest_way

    return dict_of_shortest_ways
