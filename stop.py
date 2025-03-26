import yagmail
from flask import Flask, jsonify, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates", static_folder="static")

# Email Configuration
yag = yagmail.SMTP("bhandariarnav06@gmail.com", "qkrc uqjv oygu eqqz")

# Bus Stops Data
bus_stops = {
    "andheri": [
        {"name": "Andheri Station (W)", "lat": 19.1197, "lon": 72.8466},
        {"name": "Gundavali Bus Stop Andheri East", "lat": 19.1180, "lon": 72.8510},
        {"name": "Andheri Bus Station (E) Agarkar Chowk", "lat": 19.1150, "lon": 72.8530}
    ],
    "vileparle": [
        {"name": "Vile Parle Station (E)", "lat": 19.1000, "lon": 72.8370},
        {"name": "Hanuman Road Bus Stop", "lat": 19.1020, "lon": 72.8390},
        {"name": "Vile Parle Station (E)", "lat": 19.1000, "lon": 72.8370}
    ],
    "santacruz": [
        {"name": "Santacruz Bus Station (E)", "lat": 19.0800, "lon": 72.8550},
        {"name": "Santacruz Station (W)", "lat": 19.0780, "lon": 72.8500},
        {"name": "Santacruz Station (East)", "lat": 19.0790, "lon": 72.8560}
    ]
}

# Generate bus timings dynamically
def generate_bus_timings():
    base_time = datetime.now().replace(second=0, microsecond=0)
    return [(base_time + timedelta(minutes=5 * i)).strftime("%I:%M %p") for i in range(1, 4)]

# Bus Routes Data
bus_routes = {
    1: {"route": [(19.1000, 72.8370), (19.0900, 72.8450), (19.0800, 72.8550)], "timings": generate_bus_timings()},
    2: {"route": [(19.0800, 72.8550), (19.0990, 72.8600), (19.1197, 72.8466)], "timings": generate_bus_timings()},
    3: {"route": [(19.1000, 72.8370), (19.1100, 72.8420), (19.1197, 72.8466)], "timings": generate_bus_timings()}
}

# Bus Data (Simulating real-time movement)
TOTAL_SEATS = 15
buses = [
    {"id": 1, "route": 1, "current_index": 0, "occupied_seats": set()},
    {"id": 2, "route": 2, "current_index": 0, "occupied_seats": set()},
    {"id": 3, "route": 3, "current_index": 0, "occupied_seats": set()}
]

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/mumbai-buses", methods=["GET"])
def get_bus_data():
    response_buses = []
    for bus in buses:
        route_info = bus_routes[bus["route"]]
        
        # Ensure smooth bus movement in sequence
        if bus["current_index"] < len(route_info["route"]) - 1:
            bus["current_index"] += 1
        else:
            bus["current_index"] = 0  # Reset to start

        lat, lon = route_info["route"][bus["current_index"]]
        timings = route_info["timings"]

        response_buses.append({
            "id": bus["id"],
            "route": bus["route"],
            "lat": lat,
            "lon": lon,
            "timings": timings,
            "occupied_seats": list(bus["occupied_seats"])
        })
    
    return jsonify({"buses": response_buses})

@app.route("/nearest-stops", methods=["POST"])
def get_nearest_stops():
    data = request.json
    location = data.get("location", "").lower()
    stops = bus_stops.get(location, [])
    return jsonify({"stops": stops})

@app.route("/send-boarding-email", methods=["POST"])
def send_boarding_email():
    data = request.json
    selected_bus_id = data.get("bus_id")

    if selected_bus_id is None:
        return jsonify({"error": "Bus ID is missing"}), 400

    try:
        selected_bus_id = int(selected_bus_id)  # Ensure it's an integer
        if selected_bus_id not in bus_routes:
            return jsonify({"error": f"Bus ID {selected_bus_id} not found"}), 400
        
        bus_timings = bus_routes[selected_bus_id]["timings"]
    except ValueError:
        return jsonify({"error": "Invalid Bus ID"}), 400

    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PAYMENT_LINK_HERE"

    email_content = f"""
    <h3>Bus Boarding Confirmation</h3>
    <p><b>Bus ID:</b> {selected_bus_id}</p>
    <p><b>Source:</b> {data.get('source', 'Unknown')}</p>
    <p><b>Nearest Stop:</b> {data.get('nearest_stop', 'Unknown')}</p>
    <p><b>Destination:</b> {data.get('destination', 'Unknown')}</p>
    <p><b>Boarding Time:</b> {data.get('boarding_time', 'Unknown')}</p>
    <p><b>Bus Timings:</b> {', '.join(bus_timings)}</p>
    <p>Scan the QR code below for payment:</p>
    <img src="{qr_code_url}" alt="Payment QR Code">
    """

    try:
        yag.send(["Kkalash.bheda@gmail.com", "arnavbhandari1609@gmail.com"], "Bus Boarding Confirmation", email_content)
        return jsonify({"message": "Boarding confirmation email sent successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
