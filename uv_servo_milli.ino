void setup() {
  // Start the Serial communication at 115200 baud rate
  Serial.begin(115200);
}

void loop() {
  // Print "Hello" to the Serial Monitor
  Serial.println("Hello");
  
  // Wait for 1 second before printing again
  delay(1000);
}
