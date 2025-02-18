import streamlit as st
import requests
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def get_distance_matrix(locations, api_key):
    url = f"https://api.tomtom.com/routing/matrix/2?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
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
        st.error(f"Error {response.status_code}: {response.text}")
        return None

def create_data_model(distance_matrix, demands, vehicle_capacity, num_vehicles):
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = distance_matrix
    data["demands"] = demands
    data["vehicle_capacities"] = [vehicle_capacity] * num_vehicles
    data["num_vehicles"] = num_vehicles
    data["depot"] = 0
    return data

def solve_cvrp(data):
    """Solves the CVRP problem and returns a string with the solution."""
    manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), 
                                           data["num_vehicles"], 
                                           data["depot"])
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
        demand_callback_index,
        0,  # null capacity slack
        data["vehicle_capacities"],
        True,  # start cumul to zero
        "Capacity",
    )
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(1)
    
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        result = ""
        total_distance = 0
        total_load = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            route_output = f"Route for vehicle {vehicle_id}:\n"
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data["demands"][node_index]
                route_output += f" {node_index} Load({route_load}) -> "
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            route_output += f" {manager.IndexToNode(index)} Load({route_load})\n"
            route_output += f"Distance of the route: {route_distance}m\n"
            route_output += f"Load of the route: {route_load}\n\n"
            result += route_output
            total_distance += route_distance
            total_load += route_load
        result += f"Total distance of all routes: {total_distance}m\n"
        result += f"Total load of all routes: {total_load}\n"
        return result
    else:
        return "No solution found!"

def main():
    st.title("CVRP Solver")
    st.write("Input the parameters for the CVRP problem below.")

    api_key = st.text_input("TomTom API Key", type="password")
    num_vehicles = st.number_input("Number of vehicles", min_value=1, value=2, step=1)
    vehicle_capacity = st.number_input("Vehicle capacity", min_value=1, value=5, step=1)
    num_locations = st.number_input("Number of locations", min_value=2, value=3, step=1)
    
    st.write("Enter the details for each location. (Note: Location 0 is the depot.)")
    locations = []
    demands = []
    for i in range(num_locations):
        st.subheader(f"Location {i}")
        lat = st.number_input(f"Latitude for location {i}", value=0.0, format="%.6f", key=f"lat_{i}")
        lon = st.number_input(f"Longitude for location {i}", value=0.0, format="%.6f", key=f"lon_{i}")
        demand = st.number_input(f"Demand for location {i}", min_value=0, value=0, step=1, key=f"demand_{i}")
        locations.append((lat, lon))
        demands.append(demand)
    
    if st.button("Solve CVRP"):
        if not api_key:
            st.error("Please enter a valid TomTom API Key.")
            return
        
        distance_matrix = get_distance_matrix(locations, api_key)
        if distance_matrix is None:
            st.error("Failed to retrieve the distance matrix.")
            return
        
        data = create_data_model(distance_matrix, demands, vehicle_capacity, num_vehicles)
        result = solve_cvrp(data)
        st.text_area("Solution", result, height=300)

if __name__ == "__main__":
    main()
