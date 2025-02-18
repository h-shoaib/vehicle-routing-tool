import numpy as np
from pyvrp import Model, VehicleType, Client
from pyvrp.stop import MaxRuntime  # Correct stopping condition

# Define the time matrix (including depot at index 0)
time_matrix = np.array([
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
])

# Define customer demands (0 for depot)
demands = [0, 5, 10, 8]  

# Define vehicle parameters
vehicle_capacity = 15  
num_vehicles = 2  

# Create a model
model = Model()

# ✅ Corrected VehicleType initialization
vehicle_type = VehicleType(
    capacity=[vehicle_capacity],  # Must be a list
    start_depot=0,  # Vehicles start at depot (index 0)
    end_depot=0,    # Vehicles return to depot (index 0)
    max_duration=1000,  # Max allowed route duration
    max_distance=1000   # Max allowed route distance
)

# ✅ Add vehicle type correctly (num_available is specified here, NOT inside VehicleType)
for _ in range(num_vehicles):
    model.add_vehicle_type(vehicle_type)

# ✅ Add clients (excluding depot)
for i in range(1, len(time_matrix)):
    model.add_client(Client(
        index=i,
        demand=demands[i],
        service_duration=5,  # Service time at each stop
        tw_early=0,  # Earliest service time
        tw_late=100  # Latest service time
    ))

# ✅ Set depot
model.set_depot(Client(index=0))

# ✅ Set travel costs (time-based)
model.set_travel_costs(lambda i, j: time_matrix[i, j])

# ✅ Solve the VRP with correct stopping condition
solution = model.solve(stop=MaxRuntime(1.0))  # Stops after 1 second of computation

# ✅ Print results
if solution:
    print(f"Total Cost: {solution.cost()}")
    for route in solution.routes():
        print(f"Route: {route.nodes()}")
else:
    print("No solution found!")
