import requests
import random
import json
from azure.iot.device import Message, IoTHubDeviceClient
from datetime import datetime
import time

BACKEND_URL = 'http://localhost:5000/api/simulator/devices'

response = requests.get(BACKEND_URL).json()
devices = response['data']

def generate_value(prev, min_v, max_v):
    variation = (max_v - min_v) * 0.05
    value = prev + random.uniform(-variation, variation)
    return round(max(min_v, min(value, max_v)), 2)

def get_last_value(sensor_id):
    url = f'http://localhost:5000/api/simulator/sensor/{sensor_id}'
    request = requests.get(url, timeout=2)
    if request.status_code == 200:
        return request.json()['telemetry']['value']
    return None

def generate_payload(device):
    payload = {
        'timestamp': datetime.utcnow().isoformat(),
        'device_id' : device['device_id']
    }
    client = IoTHubDeviceClient.create_from_connection_string(device['connection_string'])

    for sensor in device['sensors']:
        last_value = get_last_value(sensor['id'])
        if last_value is not None:
            initial_value = last_value
        else:
            initial_value = random.uniform(sensor['min_value'], sensor['max_value'])
        payload['sensor'] = sensor['id']
        try:
            while True:
                value = generate_value(initial_value, sensor['min_value'], sensor['max_value'])
                initial_value = value
                payload['value'] = value
                message = Message(json.dumps(payload))
                message.content_encoding = 'utf-8'
                message.content_type = 'application/json'
                client.send_message(message)
                time.sleep(random.randint(5, 30))
        except KeyboardInterrupt:
            print(f"[{device['device_id']}] stopped")
        finally:
            client.shutdown()                

if __name__ == '__main__':
    for device in devices:
        generate_payload(device)
                