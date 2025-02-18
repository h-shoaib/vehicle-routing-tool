import requests

API_KEY = "7wIOKkBuughA4UKf04vLlhecCuOWZT5K"

def get_travel_matrix(locations):
    
    url = f"https://api.tomtom.com/routing/matrix/2?key={API_KEY}"
    
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
            print("Error: 'data' key not found in API response!")
            return None

        print("\n🚗 Travel Time Matrix (in minutes):")

        
        for entry in data["data"]:
            origin_idx = entry["originIndex"]
            destination_idx = entry["destinationIndex"]
            
            
            if origin_idx != destination_idx:
                travel_time_seconds = entry["routeSummary"]["travelTimeInSeconds"]
                travel_time_minutes = travel_time_seconds // 60
                
                print(f"{locations[origin_idx]} → {locations[destination_idx]}: {travel_time_minutes} min")

        return data["data"]

    else:
        print(f" Error {response.status_code}: {response.text}")
        return None

locations = [
    (25.27784594609928, 55.373069148949476),  # home
    (25.27801591137463, 55.346953566319705),  # vzone
    (25.29769325918848, 55.3735023190593340)  # sahara center
]


travel_matrix = get_travel_matrix(locations)

print(travel_matrix)