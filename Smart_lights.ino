// Define the pin numbers
const int ldrPin = A0;      // LDR connected to analog pin A0
const int ledPin = 9;       // LED connected to PWM digital pin 9
const int trigPin = 10;     // Trigger pin for ultrasonic sensor
const int echoPin = 11;     // Echo pin for ultrasonic sensor

// Define a constant for maximum brightness
const int maxBrightness = 255; // Maximum brightness for PWM

// Variables for timing
unsigned long previousMillis = 0; // Store the last time the loop was executed
const long interval = 500000;      // Interval at which to read (in microseconds)
const long printDelay = 1000;      // Delay between prints (in milliseconds)

void setup() {
  // Initialize the LED pin as an output
  pinMode(ledPin, OUTPUT);
  // Initialize the ultrasonic sensor pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  // Start the serial communication for debugging
  Serial.begin(9600);
}

void loop() {
  // Measure distance using the ultrasonic sensor
  long duration, distance;

  // Clear the trigger
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Set the trigger to HIGH for 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Read the echo pin
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance in cm
  distance = duration * 0.034 / 2; // Speed of sound is 0.034 cm/µs
  
  // Print the distance to the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
  
  // Check if the object is within 15 cm
  if (distance <= 15) {
    // Read the value from the LDR
    int ldrValue = analogRead(ldrPin);
    
    // Print the LDR value to the Serial Monitor
    Serial.print("LDR Value: ");
    Serial.println(ldrValue);
    
    // Calculate brightness using a simpler formula
    int brightness = maxBrightness - (ldrValue / 4.01); // Inverse relationship
    
    // Ensure brightness is within the valid range
    brightness = constrain(brightness, 0, maxBrightness);
    
    // Set the LED brightness using PWM
    analogWrite(ledPin, brightness);
  } else {
    // If the object is farther than 15 cm, turn off the LED
    analogWrite(ledPin, 0);
    Serial.println("LED turned off: Object is farther than 15 cm.");
  }
  
  // Delay between prints to the Serial Monitor
  delay(printDelay); // Delay for 1000 milliseconds (1 second)
}
