from extensions import redis_client

def cache_device(device):
    redis_client.hset(
        f"device:{device.id}",
        mapping={
            'name': device.name,
            'status': device.status,
            'owner': device.user_id
        }
    )

def delete_device_cache(device_id):
    sensor_ids = redis_client.smembers(f"device:{device_id}:sensors")

    for sid in sensor_ids:
        redis_client.delete(f"sensor:{sid}")

    redis_client.delete(f"device:{device_id}:sensors")
    redis_client.delete(f"device:{device_id}")

def cache_sensor(sensor):
    redis_client.hset(
        f"sensor:{sensor.id}",
        mapping={
            'device': sensor.device_id,
            'name': sensor.name,
            'unit': sensor.unit
        }
    )
    redis_client.sadd(
        f'device:{sensor.device_id}:sensors',
        sensor.id
    )

def delete_sensor_cache(sensor_id, device_id=None):
    redis_client.delete(f"sensor:{sensor_id}")

    if device_id:
        redis_client.srem(
            f"device:{device_id}:sensors",
            sensor_id
        )


def cache_rule(rule):
    if not rule.enabled:
        return 
    
    mapping={
        'message': rule.message
    }

    if rule.sensor_id is not None:
        mapping['sensor_id'] = rule.sensor_id
        redis_client.sadd(
            f'sensor:{rule.sensor_id}:rules',
            rule.id
        )

    if rule.sensor_name is not None:
        mapping['sensor_name'] = rule.sensor_name
        redis_client.sadd(
            f'sensor:{rule.sensor_name}:rules',
            rule.id
        )

    if rule.min_value is not None:
        mapping['min_value'] = rule.min_value

    if rule.max_value is not None:
        mapping['max_value'] = rule.max_value

    redis_client.sadd(f'org:{rule.organization}:rules:enabled', rule.id)

    redis_client.hset(
        f'rule:{rule.id}',
        mapping=mapping
    )

def delete_rule_cache(rule_id, sensor_id=None):
    redis_client.delete(f"rule:{rule_id}")

    if sensor_id:
        redis_client.srem(
            f"sensor:{sensor_id}:rules",
            rule_id
        )

def clear_rule_cache():
    patterns = [
        'rule:*',
        'sensor:*:rules',
        'sensor_name:*:rules',
        'org:*:rules:enabled'
    ]
    for pattern in patterns:
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
