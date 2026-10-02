import csv
import math


def load_places(filename):
    places = {}
    file = open(filename, newline="", encoding="utf-8-sig")
    reader = csv.DictReader(file)
    for row in reader:
        places[row["id"]] = {
            "name": row["name"],
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "type": row["type"]
        }
    file.close()
    return places


def load_roads(filename):
    roads = []
    file = open(filename, newline="", encoding="utf-8-sig")
    reader = csv.DictReader(file)
    for row in reader:
        roads.append((row["from_id"], row["to_id"], float(row["distance_km"])))
    file.close()
    return roads


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # radius of earth in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def build_graph(places, roads):
    graph = {}
    for place_id in places:
        graph[place_id] = {}

    for from_id, to_id, distance in roads:
        graph[from_id][to_id] = distance
        graph[to_id][from_id] = distance  # road works both ways

    return graph

def get_hospitals(places):
    hospitals = []
    for place_id in places:
        if places[place_id]["type"] == "hospital":
            hospitals.append(place_id)
    return hospitals

def build_heuristic(places, goal_id):
    heuristic = {}
    goal_lat = places[goal_id]["lat"]
    goal_lon = places[goal_id]["lon"]

    for place_id in places:
        lat = places[place_id]["lat"]
        lon = places[place_id]["lon"]
        heuristic[place_id] = haversine(lat, lon, goal_lat, goal_lon)

    return heuristic


# quick test
if __name__ == "__main__":
    places = load_places("data/places.csv")
    roads = load_roads("data/roads.csv")
    graph = build_graph(places, roads)

    print("Places loaded:", len(places))
    print("Roads loaded:", len(roads))
    print("Example neighbors of N1:", graph.get("N1"))
