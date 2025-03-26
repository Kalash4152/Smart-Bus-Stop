#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 10
#define RST_PIN 9
#define SERVO_PIN 6  // Servo connected to Pin 6
#define LCD_ADDR 0x27  // I2C address of the LCD (Change if needed)

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
Servo myServo;  // Create Servo object
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);  // 16x2 LCD at I2C address 0x27

String lastCardUID = "";  // Store the last scanned card UID
bool paymentDone = false;  // Track payment status

void setup() {
    Serial.begin(9600);
    SPI.begin();
    mfrc522.PCD_Init();
    myServo.attach(SERVO_PIN);  // Attach servo to Pin 6
    myServo.write(0);  // Start servo at 0 degrees

    // Initialize LCD
    lcd.init();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Type 'yes' if");
    lcd.setCursor(0, 1);
    lcd.print("paid in Serial");

    Serial.println("Please type 'yes' in Serial Monitor if the amount is paid:");
}

void loop() {
    if (!paymentDone) {
        if (Serial.available()) {
            String input = Serial.readStringUntil('\n');  // Read user input
            input.trim();  // Remove extra spaces or newlines

            if (input.equalsIgnoreCase("yes")) {
                Serial.println("Payment received. You can now scan your card.");
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("Payment received");
                lcd.setCursor(0, 1);
                lcd.print("Scan your card.");
                paymentDone = true;  // Allow scanning
            } else {
                Serial.println("Please pay");
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("Please pay");
            }
        }
        return;  // Skip RFID scanning until payment is done
    }

    // Check if a new card is present
    if (!mfrc522.PICC_IsNewCardPresent()) return;
    if (!mfrc522.PICC_ReadCardSerial()) return;

    // Read UID
    String cardUID = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        cardUID += String(mfrc522.uid.uidByte[i], HEX);
        if (i < mfrc522.uid.size - 1) cardUID += " ";
    }

    cardUID.toUpperCase();  // Convert to uppercase for matching

    // Check for the specific UID
    if (cardUID == "7D C0 29 3") {  // Change to your card's UID
        if (cardUID == lastCardUID) {
            Serial.println("Thank you");
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Thank you");
        } else {
            Serial.println("Welcome");
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Welcome");

            myServo.write(90);  // Rotate servo to 90 degrees
            delay(2000);  // Hold position for 2 seconds
            myServo.write(0);  // Reset servo to 0 degrees
            lastCardUID = cardUID;  // Store the scanned card UID
        }
    } else {
        Serial.print("Card UID: ");
        Serial.println(cardUID);
        Serial.println("Please register and pay first");

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Card UID:");
        lcd.setCursor(0, 1);
        lcd.print(cardUID);
        delay(2000);

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Register & Pay");

        lastCardUID = "";  // Reset last card UID if an unknown card is detected
    }

    mfrc522.PICC_HaltA();  // Stop reading
}
