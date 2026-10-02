import random
import copy

from data_loader import build_heuristic


def astar(graph, start, goal, heuristic):
    open_list = [start] # nodes waiting to be checked
    visited = []      # nodes already fully checked
    g_cost = {start: 0}   # cheapest known cost from start to each node
    came_from = {}

    while len(open_list) > 0:
         # node in open_list with the lowest f = g + h
        current = open_list[0]
        for node in open_list:
            f_current = g_cost[current] + heuristic[current]
            f_node = g_cost[node] + heuristic[node]
            if f_node < f_current:
                current = node
          # Goal reached — rebuild and return the path
        if current == goal:
            return build_path(came_from, start, goal), g_cost[current]

        open_list.remove(current)
        visited.append(current)

        for neighbor, road_cost in graph[current].items():
            if neighbor in visited:
                continue
            new_cost = g_cost[current] + road_cost
            if neighbor not in g_cost or new_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_cost
                came_from[neighbor] = current
                if neighbor not in open_list:
                    open_list.append(neighbor)

    return None, None


def build_path(came_from, start, goal):
    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path


def apply_closures(graph, closure_chance=0.1):
    """
    Randomly closes some roads before a search.
    closure_chance is the probability any given road is closed (0.1 = 10%).

    Returns a NEW graph — the original graph passed in is left untouched,
    so you can call this fresh before every astar() run.
    """
    new_graph = copy.deepcopy(graph)
    closed_pairs = set()

    # decide once per road, not once per direction, so a closed road
    # is closed both ways instead of only blocking traffic one way
    for node in graph:
        for neighbor in graph[node]:
            pair = tuple(sorted([node, neighbor]))
            if pair in closed_pairs:
                continue
            if random.random() < closure_chance:
                closed_pairs.add(pair)

    for a, b in closed_pairs:
        if b in new_graph[a]:
            del new_graph[a][b]
        if a in new_graph[b]:
            del new_graph[b][a]

    return new_graph, closed_pairs


TRAFFIC_MULTIPLIERS = {
    "low": 1.0,
    "medium": 1.5,
    "high": 2.0,
}


def apply_traffic(graph):
    """
    Randomly assigns a traffic level to every road and scales its cost.
    Low = x1.0, Medium = x1.5, High = x2.0 (matches the project's cost model).

    Returns a NEW graph with scaled costs, plus a dict of what traffic
    level was picked for each road, e.g. {("N1", "N2"): "high"}, so
    gui.py can display it to the user.

    Like apply_closures, this decides traffic per ROAD, not per direction —
    a jammed road is jammed both ways, not just one.
    """
    new_graph = copy.deepcopy(graph)
    traffic_levels = {}

    for node in graph:
        for neighbor, base_cost in graph[node].items():
            pair = tuple(sorted([node, neighbor]))
            if pair in traffic_levels:
                level = traffic_levels[pair]
            else:
                level = random.choice(["low", "medium", "high"])
                traffic_levels[pair] = level

            multiplier = TRAFFIC_MULTIPLIERS[level]
            new_graph[node][neighbor] = base_cost * multiplier

    return new_graph, traffic_levels


def find_nearest_hospital(graph, start, hospitals, places):
    """
    Runs astar() once per hospital and keeps whichever one comes back
    cheapest. Needs `places` (from data_loader.py) to build a fresh
    heuristic dict for each hospital, since the heuristic is tied to
    one specific goal at a time.

    Returns (best_hospital_id, best_path, best_cost).
    If no hospital is reachable at all, returns (None, None, None).
    """
    best_hospital = None
    best_path = None
    best_cost = None

    for hospital_id in hospitals:
        heuristic = build_heuristic(places, hospital_id)
        path, cost = astar(graph, start, hospital_id, heuristic)

        if path is None:
            continue  # this hospital isn't reachable, skip it

        if best_cost is None or cost < best_cost:
            best_hospital = hospital_id
            best_path = path
            best_cost = cost

    return best_hospital, best_path, best_cost