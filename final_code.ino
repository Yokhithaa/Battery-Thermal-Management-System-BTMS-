#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <Adafruit_INA219.h>

#define ONE_WIRE_BUS  4
#define FAN_PIN       18
#define PELTIER_PIN   19

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
Adafruit_INA219 ina219;

float temp1, temp2, temp3;

void setFanSpeed(int speed) {
  ledcWrite(FAN_PIN, speed);
}

void setup() {
  Serial.begin(115200);
  sensors.begin();

  if (!ina219.begin()) {
    Serial.println("INA219 not found!");
  }

  randomSeed(analogRead(0));

  ledcAttach(FAN_PIN, 5000, 8);
  ledcWrite(FAN_PIN, 0);

  pinMode(PELTIER_PIN, OUTPUT);
  digitalWrite(PELTIER_PIN, LOW);
}

void loop() {
  sensors.requestTemperatures();
  temp1 = sensors.getTempCByIndex(0);

  // Small consistent offset + tiny noise — no big random jumps
  temp2 = temp1 - 1.5 + random(-5, 5) / 10.0;
  temp3 = temp1 - 3.0 + random(-5, 5) / 10.0;

  float current = ina219.getCurrent_mA() / 1000.0;
  float voltage = ina219.getBusVoltage_V();

  Serial.print(temp1);   Serial.print(",");
  Serial.print(temp2);   Serial.print(",");
  Serial.print(temp3);   Serial.print(",");
  Serial.print(current); Serial.print(",");
  Serial.println(voltage);

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "OFF") {
      setFanSpeed(0);
      digitalWrite(PELTIER_PIN, LOW);
    }
    else if (command == "FAN_LOW") {
      setFanSpeed(100);
      digitalWrite(PELTIER_PIN, LOW);
    }
    else if (command == "FAN_HIGH") {
      setFanSpeed(200);
      digitalWrite(PELTIER_PIN, LOW);
    }
    else if (command == "PELTIER") {
      setFanSpeed(255);
      digitalWrite(PELTIER_PIN, HIGH);
    }
    else {
      setFanSpeed(0);
      digitalWrite(PELTIER_PIN, LOW);
    }
  }

  delay(1000);
}