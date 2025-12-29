'use client';

import { useState, useEffect } from "react";
import axios from "axios";
import AddSensorForm from "@/app/components/add-sensor";

function DevicePage({params}){
    const [device, setDevice] = useState('');
    const [sensors, setSensors] = useState([]);
    const [visibleForm, setVisibleForm] = useState(false);

    useEffect(() => {
        async function fetchParams() {
            const deviceId = await params;
            const device_url = (`http://localhost:5000/api/device/${decodeURIComponent(deviceId.deviceId)}`);
            const sensors_url = (`http://localhost:5000/api/sensors/device/${decodeURIComponent(deviceId.deviceId)}`);
            axios.get(device_url)
            .then(response => {
                setDevice(response.data.device);
            })
            .catch(error => {
                console.error('Error on fetching device:', error);
            })
            axios.get(sensors_url)
            .then(response => {
                setSensors(response.data.sensors);
            })
            .catch(error => {
                console.error('Error on fetching sensors:', error);
            })
        }
        fetchParams();
    }, [params])

    return(
        <div className="device-page">
            <div className="device-page-card">
                <h1 className="device-title">{device.name}</h1>
                <p className="device-description">{device.description}</p>
                <div className="device-map">
                    <iframe
                        width="100%"
                        height="300"
                        style={{ border: 0, borderRadius: '12px' }}
                        loading="lazy"
                        referrerPolicy="no-referrer-when-downgrade"
                        src={`https://www.google.com/maps?q=${device.latitude},${device.longitude}&z=10&output=embed&hl=en`}
                    />
                </div>
                <div className="device-meta">
                    <p>
                        <span>Status:</span>
                        <span className={`status ${device.status}`}>{device.status}</span>
                    </p>
                    <p>
                        <span>Created at:</span>
                        {device.created_at}
                    </p>
                    <p>
                        <span>Last activity:</span>
                        {device.last_seen_at}
                    </p>
                </div>
                <div className="device-sensors">
                    <div className="sensors-header">
                        <p className="sensors-title">Connected sensors</p>
                        <button className="add-sensors-btn" onClick={() => setVisibleForm(true)}>Add sensors</button>
                    </div>
                    {sensors.length > 0 ? (
                        <div className="sensors-list">
                            {sensors.map(sensor => (
                                <span key={sensor.id} className="sensor-badge">
                                    {sensor.name}
                                </span>
                            ))}
                        </div>
                    ) : (
                        <p className="sensors-empty">
                            There are no sensors connected to this device
                        </p>
                    )}
                    <AddSensorForm visible={visibleForm} setVisible={setVisibleForm} deviceId={device.id} />
                </div>
            </div>
        </div>
    )
}

export default DevicePage;