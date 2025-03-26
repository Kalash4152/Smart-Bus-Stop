import json
import os
import smtplib
import time
from email.mime.text import MIMEText
from datetime import datetime
from threading import Timer

# Files to store data
PASSENGER_FILE = "passenger_data.json"

# Bus Settings
TOTAL_SEATS = 15
STATIONS = ["A", "B", "C"]  # Only 3 stations
current_station = 0  # Start at Station A
occupied_seats = 0
passenger_data = {}

# Fare Settings
FARE_PER_STATION = 5  # ₹5 per station

# Email Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"  # Use an App Password for Gmail
EMAIL_RECEIVER = "local-authority@gmail.com"

# Function to load passenger data
def load_passenger_data():
    if os.path.exists(PASSENGER_FILE):
        with open(PASSENGER_FILE, "r") as file:
            return json.load(file)
    else:
        return {}

# Function to save passenger data
def save_passenger_data(data):
    with open(PASSENGER_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to add passengers
def add_passenger():
    global occupied_seats
    if occupied_seats < TOTAL_SEATS:
        name = input("Enter passenger name: ").strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if name not in passenger_data:
            passenger_data[name] = {
                "Name": name,
                "Checkins": 0,
                "Checkin_Timestamps": [],
                "Logout_Timestamps": [],
                "Start_Station": STATIONS[current_station],
                "End_Station": None,
                "Seat_Assigned": None
            }

        passenger_data[name]["Checkins"] += 1
        passenger_data[name]["Checkin_Timestamps"].append(timestamp)

        # Assign the first available seat
        available_seats = [i for i in range(1, TOTAL_SEATS + 1) if i not in [p["Seat_Assigned"] for p in passenger_data.values() if p["Seat_Assigned"]]]
        
        if available_seats:
            assigned_seat = available_seats[0]
            passenger_data[name]["Seat_Assigned"] = assigned_seat
            occupied_seats += 1
            print(f"🪑 Seat Assigned to {name}: {assigned_seat} at Station {STATIONS[current_station]}")
        else:
            print("⚠ No seats available.")

        save_passenger_data(passenger_data)
    else:
        print("🚨 Bus Overloaded! No more seats available.")

# Function to remove passengers when they get off
def remove_passenger():
    global occupied_seats
    print("\n🚏 Updating seats...")

    name = input("Enter passenger name who is getting off: ").strip()
    if name in passenger_data and passenger_data[name]["Seat_Assigned"] is not None:
        seat_number = passenger_data[name]["Seat_Assigned"]
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        passenger_data[name]["Logout_Timestamps"].append(logout_time)

        # Assign end station
        passenger_data[name]["End_Station"] = STATIONS[current_station]

        # Calculate fare
        start_index = STATIONS.index(passenger_data[name]["Start_Station"])
        end_index = STATIONS.index(passenger_data[name]["End_Station"])
        stations_traveled = abs(end_index - start_index)
        total_fare = stations_traveled * FARE_PER_STATION

        print(f"🚶 {name} got off at {STATIONS[current_station]}. Seat {seat_number} is now free.")
        print(f"💰 Total Fare: ₹{total_fare} (₹{FARE_PER_STATION} per station)")

        passenger_data[name]["Seat_Assigned"] = None
        occupied_seats -= 1
    else:
        print("❌ Passenger not found or already logged out!")

    save_passenger_data(passenger_data)

# Function to count passengers within a time range
def count_passengers_in_time_range(target_hour):
    count = 0
    start_time = target_hour - 0.5  # 30 minutes before
    end_time = target_hour + 0.5   # 30 minutes after

    for passenger in passenger_data.values():
        for timestamp in passenger["Checkin_Timestamps"]:
            checkin_hour = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour + \
                           datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").minute / 60
            if start_time <= checkin_hour <= end_time:
                count += 1

    return count

# Function to send email with log-in count
def send_email_logins(target_hour):
    logins_count = count_passengers_in_time_range(target_hour)
    subject = f"🚍 Bus System Logins Update ({target_hour-0.5}:30 - {target_hour+0.5}:30)"
    message = f"Total passengers logged in between {target_hour-0.5}:30 and {target_hour+0.5}:30: {logins_count}"

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print(f"📧 Email sent successfully for {target_hour-0.5}:30 - {target_hour+0.5}:30!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Schedule emails at 9:30 AM and 9:30 PM
now = datetime.now()
morning_email_time = datetime(now.year, now.month, now.day, 9, 30)  # 9:30 AM
evening_email_time = datetime(now.year, now.month, now.day, 21, 30)  # 9:30 PM

if now < morning_email_time:
    Timer((morning_email_time - now).total_seconds(), lambda: send_email_logins(9)).start()

if now < evening_email_time:
    Timer((evening_email_time - now).total_seconds(), lambda: send_email_logins(21)).start()

# Main loop
print("\n🚍 Welcome to Smart Bus System!")

try:
    while True:
        print(f"\n📍 Current Station: {STATIONS[current_station]}")

        action = input("\nChoose action: (1) Add Passenger (2) Remove Passenger (3) Next Station (4) Check 9AM/9PM count: ").strip()

        if action == "1":
            add_passenger()
        elif action == "2":
            remove_passenger()
        elif action == "3":
            current_station = (current_station + 1) % len(STATIONS)
        elif action == "4":
            count_9am = count_passengers_in_time_range(9)
            count_9pm = count_passengers_in_time_range(21)
            print(f"\n📊 Passengers logged in between 8:30 - 9:30 AM: {count_9am}")
            print(f"📊 Passengers logged in between 8:30 - 9:30 PM: {count_9pm}")
        else:
            print("❌ Invalid input!")

except KeyboardInterrupt:
    print("\n🛑 Stopping System...")
