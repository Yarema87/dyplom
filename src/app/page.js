'use client';

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import AddDeviceForm from "./components/add-device";
import Link from "next/link";
import { toast } from "react-toastify";

export default function Home() {
  const [user, setUser] = useState('');
  const [devices, setDevices] = useState([]);
  const [visibleForm, setVisibleForm] = useState(false);
  const router = useRouter();

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
                <span className="device-status active">Active</span>
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
      <AddDeviceForm visible={visibleForm} setVisible={setVisibleForm} />
    </div>
  );
}
