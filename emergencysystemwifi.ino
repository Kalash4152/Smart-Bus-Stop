#include <WiFi.h>  
#include <HTTPClient.h>

const char* ssid = "Kalash";
const char* password = "okay4152";
const char* serverUrl = "http://your-server-ip:5000/send_alert"; 

const int buttonPin = 5; 
bool buttonPressed = false;

void setup() {
    Serial.begin(115200);
    pinMode(buttonPin, INPUT_PULLUP);

    WiFi.mode(WIFI_STA); // Set ESP32 as WiFi client
    WiFi.begin(ssid, password);
    
    Serial.print("Connecting to WiFi");
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) { 
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConnected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nFailed to connect to WiFi. Restarting...");
        delay(3000);
        ESP.restart();
    }
}

void loop() {
    if (digitalRead(buttonPin) == LOW && !buttonPressed) {
        buttonPressed = true;
        sendAlert();
        delay(1000);
    }
    if (digitalRead(buttonPin) == HIGH) {
        buttonPressed = false;
    }
}

void sendAlert() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");

        String payload = "{\"bus_no\": \"1234\", \"latitude\": \"19.0760\", \"longitude\": \"72.8777\"}"; 
        int httpResponseCode = http.POST(payload);

        if (httpResponseCode > 0) {
            Serial.println("Alert sent successfully!");
        } else {
            Serial.print("Error: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi not connected!");
    }
}
