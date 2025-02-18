# IMPLEMENTED OR TOOLS IN THIS

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model():
    """Stores the data for the problem."""
    data = {
        'distance_matrix': [  # Example distance matrix
            [0, 10, 20, 30],
            [10, 0, 15, 25],
            [20, 15, 0, 18],
            [30, 25, 18, 0]
        ],
        'num_vehicles': 2,  # Number of delivery vehicles
        'depot': 0  # Start location (depot)
    }
    return data

def solve_vrp():
    """Solves the VRP using OR-Tools."""
    data = create_data_model()
    
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
            print(f"Route for vehicle {vehicle_id}: {route}")
    else:
        print("No solution found!")

solve_vrp()
