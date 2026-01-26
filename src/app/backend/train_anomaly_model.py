import numpy as np
import pandas as pd
import joblib
from keras.models import Model
from keras.layers import Input, LSTM, RepeatVector, TimeDistributed, Dense
from keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict

WINDOW_SIZE = 30
EPOCHS = 30
BATCH_SIZE = 64

df = pd.read_csv("telemetry.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

input_layer = Input(shape=(WINDOW_SIZE, 1))

encoded = LSTM(64, activation="tanh", return_sequences=False)(input_layer)
decoded = RepeatVector(WINDOW_SIZE)(encoded)
decoded = LSTM(64, activation="tanh", return_sequences=True)(decoded)
output = TimeDistributed(Dense(1))(decoded)

model = Model(input_layer, output)
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="mse"
)

def create_sequences(data, window_size):
    return np.array([
        data[i:i + window_size]
        for i in range(len(data) - window_size)
    ])


X_all = []

scalers = {}
sensor_windows = {}

for sensor_id, group in df.groupby("sensor_id"):
    values = group.sort_values("timestamp")["value"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    values_scaled = scaler.fit_transform(values)

    X_sensor = create_sequences(values_scaled, WINDOW_SIZE)

    if len(X_sensor) == 0:
        continue

    scalers[sensor_id] = scaler
    sensor_windows[sensor_id] = X_sensor
    X_all.append(X_sensor)

X_all = np.vstack(X_all)

print(f"Навчання на {len(X_all)} вікнах з {len(sensor_windows)} сенсорів")

model.fit(
    X_all,
    X_all,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_split=0.1,
    shuffle=True
)

model.save("anomaly_model.keras")
joblib.dump(scalers, "scalers.pkl")

thresholds = {}

for sensor_id, X_sensor in sensor_windows.items():
    recon = model.predict(X_sensor, batch_size=512, verbose=0)
    errors = np.mean(np.abs(X_sensor - recon), axis=(1, 2))
    thresholds[sensor_id] = np.percentile(errors, 99)

joblib.dump(thresholds, "thresholds.pkl")

print("✅ Модель, scaler-и і threshold-и збережено")
