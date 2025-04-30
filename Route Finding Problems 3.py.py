# Modifying the previous code to include round trip functionality (add a return path)
import streamlit as st
import networkx as nx
from geopy.distance import geodesic
import folium

# Define Egyptian cities with their coordinates
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

# Define city connections (edges)
edges = [
    ("Cairo", "Giza"), ("Cairo", "Tanta"), ("Cairo", "Beni Suef"),
    ("Cairo", "Fayoum"), ("Giza", "Fayoum"), ("Tanta", "Mansoura"),
    ("Tanta", "Alexandria"), ("Mansoura", "Ismailia"), ("Ismailia", "Suez"),
    ("Suez", "Cairo"), ("Alexandria", "Cairo"), ("Beni Suef", "Fayoum")
]

# Build the graph with distances as weights
G = nx.Graph()
for u, v in edges:
    distance = geodesic(coordinates[u], coordinates[v]).km
    G.add_edge(u, v, weight=round(distance, 2))

# Heuristic function using geodesic distance
def heuristic(a, b):
    return geodesic(coordinates[a], coordinates[b]).km

# Streamlit UI
st.set_page_config(page_title="Route Finder", layout="wide")
st.title("📍 Route Finder between Egyptian Cities (A* Algorithm)")

source = st.selectbox("Choose the starting city:", list(coordinates.keys()))
dest = st.selectbox("Choose the destination city:", list(coordinates.keys()))

round_trip = st.checkbox("Include return trip")

if st.button("Find Shortest Route"):
    try:
        # Find path to destination
        path_to_dest = nx.astar_path(G, source, dest, heuristic=heuristic)
        cost_to_dest = nx.astar_path_length(G, source, dest, heuristic=heuristic)

        # If return trip is selected, find path back to source
        if round_trip:
            path_to_source = nx.astar_path(G, dest, source, heuristic=heuristic)
            cost_to_source = nx.astar_path_length(G, dest, source, heuristic=heuristic)
            total_cost = cost_to_dest + cost_to_source
            path = path_to_dest + path_to_source[1:]  # Avoid duplicating the source city
            st.success(f"✅ Round trip path found: {' → '.join(path)}")
            st.info(f"🛣️ Total round trip distance: {round(total_cost, 2)} km")
        else:
            path = path_to_dest
            total_cost = cost_to_dest
            st.success(f"✅ Path found: {' → '.join(path)}")
            st.info(f"🛣️ Total distance: {round(total_cost, 2)} km")

        # Generate interactive map
        midpoint = coordinates[path[len(path) // 2]]
        m = folium.Map(location=midpoint, zoom_start=7)

        # Add city markers
        for city in coordinates:
            folium.Marker(
                location=coordinates[city],
                popup=city,
                icon=folium.Icon(color="blue" if city not in path else "red")
            ).add_to(m)

        # Draw path lines
        for i in range(len(path) - 1):
            loc1 = coordinates[path[i]]
            loc2 = coordinates[path[i + 1]]
            folium.PolyLine([loc1, loc2], color="red", weight=4).add_to(m)

        # Display map in Streamlit
        st.components.v1.html(m._repr_html_(), height=600, scrolling=False)

    except nx.NetworkXNoPath:
        st.error("⚠️ No path exists between the selected cities.")
