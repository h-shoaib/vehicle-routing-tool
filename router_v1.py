import requests

API_KEY = "7wIOKkBuughA4UKf04vLlhecCuOWZT5K"

def get_travel_time(start_lat, start_lon, end_lat, end_lon):
    
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json"
    
    params = {
        "key": API_KEY,
        "traffic": "true",  
        "routeType": "fastest",  
        "travelMode": "car" 
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "routes" in data and data["routes"]:
            travel_time_seconds = data["routes"][0]["summary"]["travelTimeInSeconds"]
            travel_time_minutes = travel_time_seconds // 60
            print(f"Estimated travel time: {travel_time_minutes} minutes")
        else:
            print("No route found. Please check your input coordinates.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

#25.27801591137463, 55.346953566319705
start_lat, start_lon = 25.27801591137463, 55.346953566319705
#25.27784594609928, 55.373069148949476
end_lat, end_lon = 25.27784594609928, 55.373069148949476


get_travel_time(start_lat, start_lon, end_lat, end_lon)