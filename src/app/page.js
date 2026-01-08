'use client';

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import axios from "axios";
import AddDeviceForm from "./components/add-device";
import Link from "next/link";
import { toast } from "react-toastify";
import Statistics from "./components/sensor-chart";

export default function Home() {
  const [user, setUser] = useState('');
  const [devices, setDevices] = useState([]);
  const [visibleForm, setVisibleForm] = useState(false);
  const [visibleList, setVisibleList] = useState(false);
  const [sensors, setSensors] = useState([]);
  const searchParams = useSearchParams();
  const router = useRouter();
  const telemetry_sensors = searchParams.get('sensors')?.split(',').filter(Boolean).map(Number) || [];

  useEffect(() => {
    const url = 'http://localhost:5000/api/dashboard';
    axios.get(url, {withCredentials: true})
    .then(response => {
      setUser(response.data.user);
    })
    .catch(error => {
      console.error('Error on fetching user:', error);
      router.push('/login');
    })
  }, [])

  useEffect(() => {
    if (!user) return;

    const url = (`http://localhost:5000/api/device/user/${user.user_id}`);
    axios.get(url)
    .then(response => {
      setDevices(response.data.devices);
    })
    .catch(error => {
      setDevices(null);
      console.error('Error on fetching user devices:', error);
    })
  }, [user])

  useEffect(() => {
        if(telemetry_sensors.length > 0){
            localStorage.setItem(
                `dashboard-sensors`, 
                JSON.stringify(telemetry_sensors)
            );
        }
    }, [telemetry_sensors])

    useEffect(() => {
        if(telemetry_sensors.length === 0){
            const saved = localStorage.getItem(`dashboard-sensors`);
            if (saved && saved.length > 0){
                router.push(`?sensors=${JSON.parse(saved).join(',')}`, {
                    scroll: false
                })
            }
        }
    }, [])

  const getDeviceSensors = (device_id) => {
    const url = (`http://localhost:5000/api/sensors/device/${device_id}`);
    axios.get(url)
    .then(response => {
      setSensors(response.data.sensors);
    })
    .catch(error => {
      console.error('Error on fetching sensors:', error);
    })
  }

  const removeDevice = (device_id) => {
    const url = (`http://localhost:5000/api/device/remove/${device_id}`);
    axios.delete(url, {
      headers: {
              'Content-Type': 'application/json'
          },
          withCredentials: true
      })
    .then(response => {
      if(response.data.success){
        toast.success('Device has been deleted');
      }
    })
    .catch(error => {
      toast.error('Something went wrong');
      console.error('Error on deleting device:', error);
    })
  }

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

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>My devices</h1>
        <button className="add-device-btn" onClick={() => setVisibleForm(true)}>
          <span>+</span>
          Add device
        </button>
      </header>
      {!devices || devices.length === 0 ? (
        <div className="empty-state">
          <h3>No devices yet</h3>
          <p>Add your first device to start monitoring sensors and collecting data.</p>
          <button className="primary-btn" onClick={() => setVisibleForm(true)}>Add your first device</button>
        </div>
      ) : (
        <div className="device-grid">
          {devices.map(device => (
            <div key={device.id} className="device-card">
              <div className="device-card-header">
                <div>
                  <h2>{device.name}</h2>
                  <p>{device.description || 'No description'}</p>
                </div>
                <span className={`status ${device.status}`}>{device.status}</span>
              </div>
              <div className="divider"></div>
              <div className="device-actions">
                <Link href={`/device/${device.id}`}><button className="link-btn">View details</button></Link>
                <button className="danger-link" onClick={() => removeDevice(device.id)}>Remove</button>
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="telemetry-section">
        <button 
        onClick={() => setVisibleList(!visibleList)}
        className="telemetry-toggle"
        >
          Customize charts
        </button>
        {visibleList && (
          <div>
            {devices.map(device => (
              <button 
              key={device.id} 
              onClick={() => getDeviceSensors(device.id)}
              className="telemetry-toggle"
              >
                {device.name}
              </button>
            ))}
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
          </div>
        )}
        <div className="telemetry-charts">
            {telemetry_sensors.map(sensor => (
              <div key={sensor}>
                <Statistics sensor_id={sensor} />
                <label>Sensor №{sensor}</label>
              </div>
            ))}
        </div>
      </div>
      <AddDeviceForm visible={visibleForm} setVisible={setVisibleForm} />
    </div>
  );
}
