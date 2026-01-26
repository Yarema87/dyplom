import pandas as pd
import random
from datetime import datetime, timedelta
import requests

BACKEND_URL = 'http://localhost:5000/api/simulator/sensors'
response = requests.get(BACKEND_URL).json()
sensors = response['data']

n = 5000
all_rows = []
initial_values = [-11, 64, 37, 42, 89, 24]

def generate_value(prev, min_v=0, max_v=100):
    variation = (max_v - min_v) * 0.01
    value = prev + random.uniform(-variation, variation)
    return round(max(min_v, min(value, max_v)), 2)

for sensor in sensors:
    current_time = datetime(2025, 1, 1)
    initial_value = initial_values[sensor['sensor_id'] - 1]
    values = []
    timestamps = []

    for _ in range(n):
        values.append(initial_value)
        timestamps.append(current_time)

        initial_value = generate_value(initial_value, sensor['min_value'], sensor['max_value'])
        delta = timedelta(seconds=random.randint(5, 30))
        current_time += delta

    for t, v in zip(timestamps, values):
        all_rows.append({
            'sensor_id': sensor['sensor_id'],
            'timestamp': t,
            'value': v
        })

df = pd.DataFrame(all_rows)
df.to_csv('telemetry.csv', index=False)
print("Дані згенеровано з рандомним інтервалом 5–30 секунд для всіх сенсорів")
