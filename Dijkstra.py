def the_best_way(graph, start_point, end_point):
    list_of_dist = [float('inf')] * len(graph.points)
    list_of_edge_to = [None] * len(graph.points)
    list_of_marks = [False] * len(graph.points)
    adjacency_list = []
    for _ in graph.points:
        adjacency_list.append([])
    for line in graph.lines:
        index_a = graph.points.index(line.points[0])
        adjacency_list[index_a].append(line)
        index_a = graph.points.index(line.points[1])
        adjacency_list[index_a].append(line)
    index_of_start = graph.points.index(start_point)
    list_of_dist[index_of_start] = 0
    while False in list_of_marks:
        list_of_active_dist = []
        for bool_idx, bol in enumerate(list_of_marks):
            if bol is False:
                list_of_active_dist.append(list_of_dist[bool_idx])
        index_of_start = list_of_dist.index(min(list_of_active_dist))
        start = graph.points[index_of_start]
        list_of_marks[index_of_start] = True
        for edge in adjacency_list[index_of_start]:
            index_of_neighbour = graph.points.index(edge.points[0 if edge.points[1] == start else 1])
            if edge.length + list_of_dist[index_of_start] < list_of_dist[index_of_neighbour]:
                list_of_edge_to[index_of_neighbour] = edge
                list_of_dist[index_of_neighbour] = edge.length + list_of_dist[index_of_start]
    shortest_way = []
    while end_point != start_point:
        idx_end_point = graph.points.index(end_point)
        part_of_the_way = list_of_edge_to[idx_end_point]
        shortest_way.append(part_of_the_way)
        intermediate_point = part_of_the_way.points[0 if part_of_the_way.points[1] == end_point else 1]
        end_point = intermediate_point
    return shortest_way[::-1]
