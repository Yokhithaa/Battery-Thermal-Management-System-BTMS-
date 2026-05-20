import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import joblib

data = pd.read_csv("battery_training.csv")

X = data[["T1","T2","T3","Current","Voltage","rise_rate"]]
y = data["Target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("R2:", model.score(X_test,y_test))
print("RMSE:", np.sqrt(mean_squared_error(y_test,y_pred)))

joblib.dump(model, "temp_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model saved")