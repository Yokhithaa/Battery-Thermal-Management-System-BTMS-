# Battery-Thermal-Management-System-BTMS-
AI-Based Battery Thermal Management System (BTMS)

An intelligent Battery Thermal Management System (BTMS) built using ESP32, DS18B20, INA219, Machine Learning, and multi-level cooling control.
The system continuously monitors battery temperature and current, predicts future thermal conditions using a GradientBoostingRegressor model, and dynamically controls a cooling fan and Peltier module to prevent overheating.

Features
Real-time battery temperature monitoring
Current and voltage sensing using INA219
Machine Learning-based temperature prediction
Temperature rise-rate calculation
Overheat prediction
Multi-level cooling control
Fan and Peltier based thermal regulation
Serial communication between ESP32 and Python
Simulated multi-cell battery monitoring using a single sensor
System Workflow
Sensors → ESP32 → Serial Data Transfer → Python ML Model
        ← Cooling Commands ← Prediction Engine
ESP32 reads:
Temperature
Current
Voltage
Data is sent to Python through serial communication.
Python:
Calculates rise rate
Predicts future temperature using GradientBoostingRegressor
Determines cooling level
Cooling command is sent back to ESP32.
ESP32 controls:
Fan speed
Peltier module
Hardware Used
Component	Purpose
ESP32	Main controller
DS18B20	Temperature sensing
INA219	Current and voltage sensing
IRLZ44N MOSFET	Switching fan and Peltier
Cooling Fan	Medium-level cooling
Peltier Module	High-level cooling
3S Li-ion Battery	Power source
Machine Learning Model
Model Used
GradientBoostingRegressor
Reason for Selection
High prediction accuracy
Handles nonlinear thermal behavior effectively
Robust against noisy sensor data
Better generalization compared to simple regression models
Input Features

The ML model uses:

[T1, T2, T3, Current, Voltage, Temperature Rise Rate]

Where:

T1 → Real sensor temperature
T2, T3 → Simulated neighboring cell temperatures
Cooling Logic
Condition	Action
Temp < 35°C	OFF
Temp > 35°C	FAN_LOW
Temp > 40°C	FAN_HIGH
Temp > 45°C	PELTIER
Serial Communication
ESP32 → Python

ESP32 sends:

T1,T2,T3,current,voltage

Example:

32.5,31.2,30.1,0.45,11.8
Python → ESP32

Python sends commands:

OFF
FAN_LOW
FAN_HIGH
PELTIER
Software Stack
Software	Purpose
Arduino IDE	ESP32 programming
Python	ML prediction and control
Scikit-learn	GradientBoostingRegressor
PySerial	Serial communication
Joblib	Model saving/loading

How It Works
1. Train the Model
python train_model.py

This generates:

temp_model.pkl
scaler.pkl
2. Upload ESP32 Code

Upload the Arduino code using Arduino IDE.

3. Run Real-Time Prediction
python realtime_prediction.py

The Python script:

Reads sensor data
Predicts temperature
Sends cooling commands
Sample Output
T1: 32.4
T2: 31.0
T3: 29.8
Current: 0.42A
Predicted Temp: 41.2°C
Cooling: FAN_HIGH
Future Improvements
WiFi/IoT dashboard integration
Real multi-cell battery pack
Cloud-based monitoring
LSTM-based thermal prediction
Mobile application support
Applications
Electric Vehicles (EVs)
Energy Storage Systems
Drones and Robotics
Portable Power Banks
Smart Battery Packs
Author

Developed by Yokhithaa
