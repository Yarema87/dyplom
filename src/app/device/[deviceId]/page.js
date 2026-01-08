'use client';

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import axios from "axios";
import AddSensorForm from "@/app/components/add-sensor";
import Link from "next/link";
import Statistics from "@/app/components/sensor-chart";

function DevicePage({params}){
    const [device, setDevice] = useState('');
    const [sensors, setSensors] = useState([]);
    const [visibleForm, setVisibleForm] = useState(false);
    const [visibleList, setVisibleList] = useState(false);
    const searchParams = useSearchParams();
    const router = useRouter();
    const telemetry_sensors = searchParams.get('sensors')?.split(',').filter(Boolean).map(Number) || [];

    const toggleSensor = (id) => {
        const updated = telemetry_sensors.includes(id) ? telemetry_sensors.filter(s => s !== id) : [...telemetry_sensors, id];
        if (updated.length === 0){
            router.push('?', {scroll: false})
        }
        else{
            router.push(
                `?sensors=${updated.join(',')}`,
                {scroll: false}
            );
        }
    };

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

    useEffect(() => {
        if(telemetry_sensors.length > 0){
            localStorage.setItem(
                `device-${device.id}-sensors`, 
                JSON.stringify(telemetry_sensors)
            );
        }
    }, [telemetry_sensors, device.id])

    useEffect(() => {
        if(telemetry_sensors.length === 0){
            const saved = localStorage.getItem(`device-${device.id}-sensors`);
            if (saved && saved.length > 0){
                router.push(`?sensors=${JSON.parse(saved).join(',')}`, {
                    scroll: false
                })
            }
        }
    }, [device.id])

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
                        {new Date(device.last_seen_at).toLocaleString()}
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
                                <Link key={sensor.id} href={`/sensor/${sensor.id}`}>
                                    <span className="sensor-badge">
                                        {sensor.name}
                                    </span>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <p className="sensors-empty">
                            There are no sensors connected to this device
                        </p>
                    )}
                    <AddSensorForm visible={visibleForm} setVisible={setVisibleForm} deviceId={device.id} />
                </div>
                <div className="telemetry-section">
                    <button 
                    className="telemetry-toggle"
                    onClick={() => setVisibleList(!visibleList)}
                    >
                        {visibleList ? 'Hide sensors list' : 'Add sensor charts'}
                    </button>
                    {visibleList && (
                        <ul className="telemetry-sensor-list">
                            {sensors.map(sensor => (
                                <li key={sensor.id} className="telemetry-sensor-item">
                                    <label>
                                        <input 
                                            type='checkbox' 
                                            checked={telemetry_sensors.includes(sensor.id)} 
                                            onChange={() => toggleSensor(sensor.id)}
                                        />
                                        <span>{sensor.name}</span>
                                    </label>
                                    
                                </li>
                            ))}
                        </ul>
                    )}
                    <div className="telemetry-charts">
                        {telemetry_sensors.map(sensor => (
                            <Statistics sensor_id={sensor} key={sensor}/>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default DevicePage;