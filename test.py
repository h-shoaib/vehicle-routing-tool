from pyvrp import Model
from pyvrp.stop import MaxIterations

# Define coordinates for each location (example: 4 locations, including the depot)
coordinates = [
    (0, 0),    # Depot at (0, 0)
    (1, 1),    # Location 1
    (2, 2),    # Location 2
    (3, 3),    # Location 3
]

# Define demands for each location
demands = [0, 10, 20, 30]  # Depot has 0 demand

# Number of vehicles and their capacity
num_vehicles = 2
vehicle_capacity = 100

# Create a model
model = Model()

# Add a vehicle type
model.add_vehicle_type(num_available=num_vehicles, capacity=[vehicle_capacity])

# Add the depot
model.add_depot(x=coordinates[0][0], y=coordinates[0][1])

# Add clients
for coord, demand in zip(coordinates[1:], demands[1:]):
    model.add_client(x=coord[0], y=coord[1], delivery=demand)

# Define a stopping criterion
stopping_criterion = MaxIterations(1000)  # Stop after 1000 iterations

# Solve the problem
solution = model.solve(stop=stopping_criterion)

# Print the solution
print("Routes:")
for route in solution.routes():
    print([client for client in route])

print(f"Total cost: {solution.cost()}")
