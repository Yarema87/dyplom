import requests
import random
import json
from azure.iot.device import Message, IoTHubDeviceClient
from datetime import datetime
import time
import threading

BACKEND_URL = 'http://localhost:5000/api/simulator/devices'

response = requests.get(BACKEND_URL).json()
devices = response['data']

def generate_value(prev, min_v, max_v):
    variation = (max_v - min_v) * 0.005
    value = prev + random.uniform(-variation, variation)
    return round(max(min_v, min(value, max_v)), 2)

def get_last_value(sensor_id):
    url = f'http://localhost:5000/api/simulator/sensor/{sensor_id}'
    request = requests.get(url, timeout=2)
    if request.status_code == 200:
        return request.json()['telemetry']['value']
    return None

def generate_payload(device):
    print('Simulation started')
    payload = {
        'device_id' : device['device_id']
    }
    client = IoTHubDeviceClient.create_from_connection_string(device['connection_string'])
    print('Client connected')
    sensor_state = {}
    for sensor in device['sensors']:
        last_value = get_last_value(sensor['id'])
        sensor_state[sensor['id']] = (
            last_value
            if last_value is not None
            else random.uniform(sensor['min_value'], sensor['max_value'])
        )
    try:
        print('Generating data')
        while True:
            for sensor in device['sensors']:
                payload['sensor'] = sensor['id']
                payload['timestamp'] = datetime.utcnow().isoformat()
                initial_value = sensor_state[sensor['id']]
                value = generate_value(initial_value, sensor['min_value'], sensor['max_value'])
                initial_value = value
                if sensor['data_type'] == 'Float':
                    payload['value'] = value
                elif sensor['data_type'] == 'Int':
                    payload['value'] = int(round(value))
                elif sensor['data_type'] == 'Boolean':
                    payload['value'] = 1 if value > 0.7 else 0
                message = Message(json.dumps(payload))
                message.content_encoding = 'utf-8'
                message.content_type = 'application/json'
                client.send_message(message)
                time.sleep(random.randint(5, 30))
    except KeyboardInterrupt:
        print('Simulation stopped')
    finally:
        client.shutdown()                

if __name__ == '__main__':
    threads = []
    for device in devices:
        t = threading.Thread(
            target=generate_payload,
            args=(device,),
            daemon=True
        )
        time.sleep(2)
        t.start()
        threads.append(t)
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print('Simulation stopped')
