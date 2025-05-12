import streamlit as st
import networkx as nx
from geopy.distance import geodesic
import folium
import heapq

coordinates = {
    "Cairo": (30.0444, 31.2357),
    "Giza": (30.0131, 31.2089),
    "Tanta": (30.7865, 31.0004),
    "Mansoura": (31.0364, 31.3807),
    "Alexandria": (31.2001, 29.9187),
    "Fayoum": (29.3084, 30.8428),
    "Beni Suef": (29.0661, 31.0994),
    "Ismailia": (30.6043, 32.2723),
    "Suez": (29.9668, 32.5498)
}

edges = [
    ("Cairo", "Giza"), ("Cairo", "Tanta"), ("Cairo", "Beni Suef"),
    ("Cairo", "Fayoum"), ("Giza", "Fayoum"), ("Tanta", "Mansoura"),
    ("Tanta", "Alexandria"), ("Mansoura", "Ismailia"), ("Ismailia", "Suez"),
    ("Suez", "Cairo"), ("Alexandria", "Cairo"), ("Beni Suef", "Fayoum")
]

G = nx.Graph()
for u, v in edges:
    distance = geodesic(coordinates[u], coordinates[v]).km
    G.add_edge(u, v, weight=round(distance, 2))

def heuristic(a, b):
    return geodesic(coordinates[a], coordinates[b]).km

def astar_algorithm(graph, start, goal):
    pq = [(heuristic(start, goal), 0, start, [start])]
    visited = set()

    while pq:
        f, g, current, path = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            return path, g

        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue
            edge_weight = graph[current][neighbor]['weight']
            new_g = g + edge_weight
            new_f = new_g + heuristic(neighbor, goal)
            heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))

    return None, float('inf')

st.set_page_config(page_title="Route Finder", layout="wide")
st.title("📍 Route Finder between Egyptian Cities (A* Algorithm)")

source = st.selectbox("Choose the starting city:", list(coordinates.keys()))
dest = st.selectbox("Choose the destination city:", list(coordinates.keys()))
round_trip = st.checkbox("Include return trip")

if st.button("Find Shortest Route"):
    try:
        path_to_dest, cost_to_dest = astar_algorithm(G, source, dest)

        if round_trip:
            path_to_source, cost_to_source = astar_algorithm(G, dest, source)
            total_cost = cost_to_dest + cost_to_source
            path = path_to_dest + path_to_source[1:]
            st.success(f" Round trip path found: {' → '.join(path)}")
            st.info(f" Total round trip distance: {round(total_cost, 2)} km")
        else:
            path = path_to_dest
            total_cost = cost_to_dest
            st.success(f" Path found: {' → '.join(path)}")
            st.info(f" Total distance: {round(total_cost, 2)} km")

        midpoint = coordinates[path[len(path) // 2]]
        m = folium.Map(location=midpoint, zoom_start=7)

        for city in coordinates:
            folium.Marker(
                location=coordinates[city],
                popup=city,
                icon=folium.Icon(color="blue" if city not in path else "red")
            ).add_to(m)

        for i in range(len(path) - 1):
            loc1 = coordinates[path[i]]
            loc2 = coordinates[path[i + 1]]
            folium.PolyLine([loc1, loc2], color="red", weight=4).add_to(m)

        st.components.v1.html(m._repr_html_(), height=600, scrolling=False)

    except nx.NetworkXNoPath:
        st.error("⚠️ No path exists between the selected cities.")
