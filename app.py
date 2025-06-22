from flask import Flask, render_template, request
import requests
from math import radians, sin, cos, sqrt, atan2
import pandas as pd

app = Flask(__name__)

def get_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': address, 'format': 'json'}
    headers = {"User-Agent": "FlaskParkingApp/1.0 (your@email.com)"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()
        return float(data[0]['lat']), float(data[0]['lon'])
    return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Load CSV once on app start
df_parkings = pd.read_csv("cleaned_parkings.csv")

@app.route("/", methods=["GET", "POST"])
def index():
    closest_parkings = []
    input_coords = None
    if request.method == "POST":
        address = request.form.get("address")
        input_coords = get_coordinates(address)
        if input_coords:
            lat_in, lon_in = input_coords
            # Calculate distance for each parking
            df_parkings["distance_km"] = df_parkings.apply(
                lambda row: haversine(lat_in, lon_in, row["lat"], row["lon"]),
                axis=1
            )
            # Sort and pick top 3 closest
            closest = df_parkings.sort_values("distance_km").head(5)
            # Convert to dicts for easier template use
            closest_parkings = closest.to_dict(orient="records")
    return render_template("index.html", parkings=closest_parkings, input_coords=input_coords)

if __name__ == "__main__":
    app.run(debug=True)
