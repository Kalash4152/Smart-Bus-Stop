#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// LCD I2C Address (usually 0x27 or 0x3F)
LiquidCrystal_I2C lcd(0x27, 16, 2);  

RTC_DS3231 rtc;   // Real-Time Clock Module
Adafruit_BME280 bme;  // BME280 Sensor

void setup() {
    Serial.begin(9600);
    Wire.begin();
    
    // Initialize LCD
    lcd.begin();
    lcd.backlight();
    
    // Initialize RTC
    if (!rtc.begin()) {
        Serial.println("RTC not found!");
        while (1);
    }

    // Initialize BME280
    if (!bme.begin(0x76)) {  // BME280 default I2C address is 0x76
        Serial.println("BME280 not found!");
        while (1);
    }
}

void loop() {
    // Get time from RTC
    DateTime now = rtc.now();
    
    // Get BME280 sensor data
    float temperature = bme.readTemperature();
    float pressure = bme.readPressure() / 100.0F;  // Convert to hPa

    // Display time on LCD
    lcd.setCursor(0, 0);
    lcd.print("Time: ");
    lcd.print(now.hour(), DEC);
    lcd.print(":");
    lcd.print(now.minute(), DEC);
    lcd.print(":");
    lcd.print(now.second(), DEC);

    // Display temperature & pressure
    lcd.setCursor(0, 1);
    lcd.print("T:");
    lcd.print(temperature, 1);
    lcd.print("C P:");
    lcd.print(pressure, 0);
    lcd.print("hPa");

    delay(1000);  // Update every second
}
