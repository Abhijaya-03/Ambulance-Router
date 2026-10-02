import streamlit as st
import matplotlib.pyplot as plt

from data_loader import load_places, load_roads, build_graph, get_hospitals
from astar import apply_closures, apply_traffic, find_nearest_hospital

st.set_page_config(page_title="Ambulance Router", page_icon="🚑", layout="centered")

# --- custom styling so it doesn't look like default Streamlit ---
st.markdown("""
<style>
.stApp {
    background-color: #e8dcc8;
}
h1 {
    font-weight: 700;
    color: #8b5e3c !important;
    margin-bottom: 0;
}
.subtitle {
    color: #7a6a55;
    font-size: 15px;
    margin-bottom: 30px;
}
div[data-testid="stSelectbox"] label {
    color: #4a3d2e;
    font-weight: 600;
}
.stButton>button {
    background-color: #8b5e3c;
    color: #fdf6ec;
    border: none;
    border-radius: 8px;
    padding: 0.6em 1.6em;
    font-weight: 600;
    width: 100%;
}
.stButton>button:hover {
    background-color: #744c2e;
}
.result-card {
    background-color: #f3e9d8;
    border: 1px solid #cbb896;
    border-radius: 14px;
    padding: 22px 26px;
    margin-top: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.result-card h3 {
    color: #6b4226;
    margin-top: 0;
}
.result-row {
    color: #4a3d2e;
    font-size: 15px;
    margin: 4px 0;
}
.result-row b {
    color: #2e2418;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    places = load_places("Data/places.csv")
    roads = load_roads("Data/roads.csv")
    graph = build_graph(places, roads)
    hospitals = get_hospitals(places)
    return places, roads, graph, hospitals


places, roads, graph, hospitals = load_data()

place_options = sorted(info["name"] for info in places.values())
name_to_id = {info["name"]: place_id for place_id, info in places.items()}

st.markdown('<h1 style="color:#8b5e3c;">🚑 Ambulance Router</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-time nearest hospital routing with live traffic & closures</div>', unsafe_allow_html=True)

selected_name = st.selectbox("Your location", options=place_options, index=None, placeholder="Type a location...")
run = st.button("Find Nearest Hospital")

if run:
    if selected_name is None:
        st.error("Please select a location first.")
    else:
        start_id = name_to_id[selected_name]

        search_graph, closed = apply_closures(graph, closure_chance=0.1)
        search_graph, traffic = apply_traffic(search_graph)

        hospital_id, path, cost = find_nearest_hospital(search_graph, start_id, hospitals, places)

        if hospital_id is None:
            st.error("No hospital is reachable — too many roads closed.")
        else:
            path_names = [places[node_id]["name"] for node_id in path]

            st.markdown(f"""
            <div class="result-card">
                <h3>🏥 {places[hospital_id]['name']}</h3>
                <div class="result-row"><b>Distance:</b> {cost:.2f} km</div>
                <div class="result-row"><b>Closed roads this search:</b> {len(closed)}</div>
                <div class="result-row"><b>Route:</b> {" → ".join(path_names)}</div>
            </div>
            """, unsafe_allow_html=True)

            # --- graph, styled to match the creamish-brown theme ---
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor("#e8dcc8")
            ax.set_facecolor("#e8dcc8")

            for from_id, to_id, _dist in roads:
                if from_id not in places or to_id not in places:
                    continue
                x = [places[from_id]["lon"], places[to_id]["lon"]]
                y = [places[from_id]["lat"], places[to_id]["lat"]]
                ax.plot(x, y, color="#c4b598", linewidth=0.8)

            path_x = [places[node_id]["lon"] for node_id in path]
            path_y = [places[node_id]["lat"] for node_id in path]
            ax.plot(path_x, path_y, color="#8b5e3c", linewidth=3, zorder=5)

            for place_id, info in places.items():
                if info["type"] == "hospital":
                    ax.scatter(info["lon"], info["lat"], facecolors="none",
                               edgecolors="#2f4858", linewidths=2, s=70, zorder=6)

            start_info = places[start_id]
            ax.scatter(start_info["lon"], start_info["lat"], color="#8b5e3c",
                       marker="*", s=180, zorder=7)

            ax.axis("off")
            st.pyplot(fig)
