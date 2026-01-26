import numpy as np
from extensions import neuromodel, scalers, thresholds

WINDOW_SIZE = 30

def create_sequences(data, window_size):
    X = []
    for i in range(len(data) - window_size):
        X.append(data[i:i + window_size])
    return np.array(X)

def compute_anomaly_score(sequence):
    seq = scalers.transform(sequence.reshape(-1, 1))
    seq = seq.reshape(1, WINDOW_SIZE, 1)

    reconstructed = neuromodel.predict(seq, verbose=0)
    loss = np.mean(np.abs(seq - reconstructed))
    return loss

def anomaly_probability(score, threshold):
    return 1 / (1 + np.exp(-(score - threshold) / threshold))

def detect_anomaly(sensor_id, values):

    if sensor_id not in scalers:
        print(f"⚠️ Нема scaler для сенсора {sensor_id}")
        return False, 0.0

    scaler = scalers[sensor_id]
    threshold = thresholds[sensor_id]

    values = np.array(values).reshape(-1, 1)

    if len(values) < WINDOW_SIZE:
        return False, 0.0

    values_scaled = scaler.transform(values)

    window = values_scaled[-WINDOW_SIZE:]
    window = window.reshape(1, WINDOW_SIZE, 1)

    reconstruction = neuromodel.predict(window, verbose=0)
    error = np.mean(np.abs(window - reconstruction))

    is_anomaly = error > threshold
    prob = min(error / threshold, 1.0)

    return {
        "is_anomaly": bool(is_anomaly),
        "probability": float(prob),
        "score": float(error)
    }