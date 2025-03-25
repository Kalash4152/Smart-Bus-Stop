#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <LiquidCrystal.h>

// Pin definitions
#define SS_PIN 10
#define RST_PIN 9
#define SERVO_PIN 6
#define LCD_RS 7
#define LCD_E 8
#define LCD_D4 4
#define LCD_D5 5
#define LCD_D6 6
#define LCD_D7 7

// Create instances
MFRC522 rfid(SS_PIN, RST_PIN);
Servo myServo;
LiquidCrystal lcd(LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

// Variables
String lastRFID = "";
bool isServoActive = false;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  myServo.attach(SERVO_PIN);
  lcd.begin(16, 2);
  lcd.print("Scan your RFID");
}

void loop() {
  // Look for a new RFID tag
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String currentRFID = "";

    // Read the RFID tag
    for (byte i = 0; i < rfid.uid.size; i++) {
      currentRFID += String(rfid.uid.uidByte[i], HEX);
    }

    // Check if the RFID is the same as the last one
    if (currentRFID == lastRFID) {
      // Same RFID scanned again
      lcd.clear();
      lcd.print("Exit");
      myServo.write(0); // Rotate servo to exit position
      isServoActive = false;
    } else {
      // New RFID scanned
      lastRFID = currentRFID;
      lcd.clear();
      lcd.print("Welcome!");
      myServo.write(90); // Rotate servo to active position
      isServoActive = true;
    }

    // Wait for a while before reading again
    delay(2000);
    rfid.PICC_HaltA();
  }
}