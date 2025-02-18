import streamlit as st
import requests
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Streamlit UI
st.title("Vehicle Routing Problem (VRP) Solver")
st.sidebar.header("Input Parameters")

# Get TomTom API Key
API = st.sidebar.text_input("Enter TomTom API Key", type="password")

# User Inputs for Locations
st.sidebar.subheader("Enter Locations (Lat, Lon)")
num_locations = st.sidebar.number_input("Number of Locations", min_value=2, max_value=10, value=3)

locations = []
for i in range(num_locations):
    lat = st.sidebar.number_input(f"Latitude {i+1}", value=25.2778 if i == 0 else 25.2976)
    lon = st.sidebar.number_input(f"Longitude {i+1}", value=55.3730 if i == 0 else 55.3735)
    locations.append((lat, lon))

# Function to get Distance Matrix
def get_distance_matrix(locations):
    if not API:
        st.error("Please enter a valid TomTom API key!")
        return None

    url = f"https://api.tomtom.com/routing/matrix/2?key={API}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "origins": [{"point": {"latitude": lat, "longitude": lon}} for lat, lon in locations],
        "destinations": [{"point": {"latitude": lat, "longitude": lon}} for lat, lon in locations]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "data" not in data:
            st.error("Error: 'data' key not found in API response!")
            return None

        size = len(locations)
        distance_matrix = [[0] * size for _ in range(size)]
        for entry in data["data"]:
            origin_idx = entry["originIndex"]
            destination_idx = entry["destinationIndex"]
            if origin_idx != destination_idx:
                travel_time_seconds = entry["routeSummary"]["travelTimeInSeconds"]
                distance_matrix[origin_idx][destination_idx] = travel_time_seconds
        return distance_matrix

    else:
        st.error(f"API Error {response.status_code}: {response.text}")
        return None

# Function to solve VRP
def solve_vrp(distance_matrix):
    data = {
        "distance_matrix": distance_matrix,
        "demands": [0] + [5] * (len(distance_matrix) - 1),
        "vehicle_capacities": [10, 10],
        "num_vehicles": 2,
        "depot": 0
    }

    manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), data["num_vehicles"], data["depot"])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, data["vehicle_capacities"], True, "Capacity"
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.FromSeconds(1)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        routes = []
        total_distance = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            route = []
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

            route.append(manager.IndexToNode(index))
            routes.append((vehicle_id, route, route_distance))
            total_distance += route_distance
        return routes, total_distance
    return None, None

# Button to Run the Optimization
if st.sidebar.button("Solve VRP"):
    st.write("Fetching Distance Matrix...")
    distance_matrix = get_distance_matrix(locations)

    if distance_matrix:
        st.success("Distance Matrix Retrieved! Solving VRP...")
        routes, total_distance = solve_vrp(distance_matrix)

        if routes:
            st.subheader("Optimized Routes")
            for vehicle_id, route, distance in routes:
                st.write(f"🚛 **Vehicle {vehicle_id}:** Route {route}, Distance: {distance}m")
            st.write(f"🏁 **Total Distance of All Routes:** {total_distance}m")
        else:
            st.error("No solution found!")
