"""
streamlit_app.py

Interactive dashboard for the Route Optimization Platform.
"""

import folium
import requests
import streamlit as st
from streamlit_folium import st_folium


API_URL = "http://127.0.0.1:8000/route-by-name"


st.set_page_config(
    page_title="Eco-Router",
    layout="wide",
)

st.title("🚗 Eco-Router")
st.markdown(
    "Find an optimized road route using machine learning and graph algorithms."
)

if "route_result" not in st.session_state:
    st.session_state.route_result = None

if "route_error" not in st.session_state:
    st.session_state.route_error = None


start_location = st.text_input(
    "Start location",
    value="India Gate, New Delhi",
    placeholder="Example: India Gate, New Delhi",
)

end_location = st.text_input(
    "Destination",
    value="Connaught Place, New Delhi",
    placeholder="Example: Connaught Place, New Delhi",
)


if st.button("Find Route", type="primary"):
    st.session_state.route_error = None

    if not start_location.strip() or not end_location.strip():
        st.session_state.route_result = None
        st.session_state.route_error = (
            "Enter both a start location and a destination."
        )
    else:
        try:
            with st.spinner("Finding locations and computing route..."):
                response = requests.post(
                    API_URL,
                    json={
                        "start_location": start_location,
                        "end_location": end_location,
                    },
                    timeout=120,
                )

            if not response.ok:
                error_detail = response.json().get(
                    "detail",
                    "The route could not be computed.",
                )
                raise ValueError(error_detail)

            st.session_state.route_result = response.json()

        except (requests.RequestException, ValueError) as error:
            st.session_state.route_result = None
            st.session_state.route_error = str(error)


if st.session_state.route_error:
    st.error(st.session_state.route_error)


if st.session_state.route_result is not None:
    result = st.session_state.route_result
    coordinates = result.get("coordinates", [])

    if len(coordinates) < 2:
        st.error("The API returned an invalid route.")
    else:
        st.success("Route Computed Successfully")

        metric_col_1, metric_col_2 = st.columns(2)

        metric_col_1.metric(
            "Predicted Cost",
            f"{result['predicted_cost']:.2f}",
        )

        metric_col_2.metric(
            "Nodes Traversed",
            result["path_length"],
        )

        route = [
            [point["lat"], point["lon"]]
            for point in coordinates
        ]

        route_map = folium.Map(
            location=route[0],
            zoom_start=14,
        )

        folium.Marker(
            route[0],
            tooltip="Start",
            icon=folium.Icon(color="green"),
        ).add_to(route_map)

        folium.Marker(
            route[-1],
            tooltip="Destination",
            icon=folium.Icon(color="red"),
        ).add_to(route_map)

        folium.PolyLine(
            route,
            weight=5,
            color="blue",
        ).add_to(route_map)

        st_folium(
            route_map,
            width=None,
            height=600,
            key="route_map",
        )