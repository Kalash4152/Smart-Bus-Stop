import yagmail
from flask import Flask, jsonify, render_template, request
import random
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates", static_folder="static")

# Email Configuration
yag = yagmail.SMTP("bhandariarnav06@gmail.com", "qkrc uqjv oygu eqqz")

# Bus Stops
bus_stops = [
    {"id": 1, "name": "Vile Parle", "lat": 19.1000, "lon": 72.8370},
    {"id": 2, "name": "Santacruz", "lat": 19.0800, "lon": 72.8550},
    {"id": 3, "name": "Andheri", "lat": 19.1197, "lon": 72.8466}
]

# Function to generate fixed bus departure timings
def generate_bus_timings():
    base_time = datetime.now().replace(second=0, microsecond=0)
    return [(base_time + timedelta(minutes=5 * i)).strftime("%I:%M %p") for i in range(1, 4)]  # Next 3 departures

# Bus Routes & Timings
bus_routes = {
    1: {"route": [(19.1000, 72.8370), (19.0900, 72.8450), (19.0800, 72.8550)], "timings": generate_bus_timings()},
    2: {"route": [(19.0800, 72.8550), (19.0990, 72.8600), (19.1197, 72.8466)], "timings": generate_bus_timings()},
    3: {"route": [(19.1000, 72.8370), (19.1100, 72.8420), (19.1197, 72.8466)], "timings": generate_bus_timings()}
}

# Buses
buses = [
    {"id": 1, "route": 1, "current_index": 0},
    {"id": 2, "route": 2, "current_index": 0},
    {"id": 3, "route": 3, "current_index": 0}
]

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/mumbai-buses", methods=["GET"])
def get_bus_data():
    response_buses = []
    for bus in buses:
        route_info = bus_routes[bus["route"]]
        bus["current_index"] = (bus["current_index"] + 1) % len(route_info["route"])
        lat, lon = route_info["route"][bus["current_index"]]
        timings = route_info["timings"]

        response_buses.append({
            "id": bus["id"],
            "route": bus["route"],
            "lat": lat,
            "lon": lon,
            "timings": timings  # Send bus timings to the frontend
        })

    return jsonify({"buses": response_buses, "stops": bus_stops})

@app.route("/nearest-stops", methods=["GET"])
def get_nearest_stops():
    random_stops = random.sample(bus_stops, 2)
    return jsonify({"stops": random_stops})

@app.route("/send-boarding-email", methods=["POST"])
def send_boarding_email():
    data = request.json

    # Get the selected bus timings
    selected_bus_id = int(data["bus_id"])
    bus_timings = next((bus_routes[bus["route"]]["timings"] for bus in buses if bus["id"] == selected_bus_id), ["No Available Buses"])

    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PAYMENT_LINK_HERE"

    email_content = f"""
    <h3>Bus Boarding Confirmation</h3>
    <p><b>Bus ID:</b> {data['bus_id']}</p>
    <p><b>Source:</b> {data['source']}</p>
    <p><b>Nearest Stop:</b> {data['nearest_stop']}</p>
    <p><b>Destination:</b> {data['destination']}</p>
    <p><b>Boarding Time:</b> {data['boarding_time']}</p>
    <p><b>Bus Timings:</b> {", ".join(bus_timings)}</p>
    <p>Scan the QR code below for payment:</p>
    <img src="{qr_code_url}" alt="Payment QR Code">
    """

    try:
        yag.send(
            to=["Kkalash.bheda@gmail.com", "arnavbhandari1609@gmail.com"],
            subject="Bus Boarding Confirmation",
            contents=email_content
        )
        return jsonify({"message": "Boarding confirmation email sent successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
