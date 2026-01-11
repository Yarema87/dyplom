'use client';

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import Link from "next/link";

function AdminPage(){
    const [activeTab, setActiveTab] = useState('operators');
    const [user, setUser] = useState('');
    const [operators, setOperators] = useState([]);
    const [devices, setDevices] = useState([]);
    const [sensors, setSensors] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const router = useRouter();

    useEffect(() => {
        const url = 'http://localhost:5000/api/dashboard/admin';
        axios.get(url, {withCredentials: true})
        .then(response => {
            setUser(response.data.user);
        })
        .catch(error => {
            console.error('Error on fetching user:', error);
            router.push('/');
        })
    }, [])

    useEffect(() => {
        const operators_url = 'http://localhost:5000/api/admin/operators';
        axios.get(operators_url, {withCredentials: true})
        .then(response => {
            setOperators(response.data.operators);
        })
        .catch(error => {
            console.error('Error on fetching operators:', error);
        })

        const devices_url = 'http://localhost:5000/api/admin/devices';
        axios.get(devices_url, {withCredentials: true})
        .then(response => {
            setDevices(response.data.devices);
        })
        .catch(error => {
            console.error('Error on fetching devices:', error);
        })

        const sensors_url = 'http://localhost:5000/api/admin/sensors';
        axios.get(sensors_url, {withCredentials: true})
        .then(response => {
            setSensors(response.data.sensors);
        })
        .catch(error => {
            console.error('Error on fetching sensors:', error);
        })
    }, [])

    return(
        <div className="admin-page">
            <nav className="admin-nav">
                <button 
                onClick={() => setActiveTab('operators')} 
                className={activeTab === 'operators' ? 'active' : ''}
                >
                    Operators
                </button>
                <button 
                onClick={() => setActiveTab('devices')}
                className={activeTab === 'devices' ? 'active' : ''}
                >
                    Devices
                </button>
                <button 
                onClick={() => setActiveTab('sensors')}
                className={activeTab === 'sensors' ? 'active' : ''}
                >
                    Sensors
                </button>
                <button 
                onClick={() => setActiveTab('alerts')}
                className={activeTab === 'alerts' ? 'active' : ''}
                >
                    Alerts
                </button>
            </nav>
            <section className={`admin-section ${activeTab === 'operators' ? '' : 'invisible'}`}>
                <h2>Operators</h2>
                <table className="admin-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Status</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {operators.map(operator => (
                            <tr key={operator.id}>
                                <td>{operator?.name}</td>
                                <td>{operator?.email}</td>
                                <td>{operator.status ? 'Approved' : 'Not approved'}</td>
                                <td><button className="approve">{operator.status ? 'Dismiss' : 'Approve'}</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>
            <section className={`admin-section ${activeTab === 'devices' ? '' : 'invisible'}`}>
                <h2>Devices</h2>
                <table className="admin-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Last seen</th>
                            <th>Operator</th>
                            <th></th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices.map(device => (
                            <tr key={device.id}>
                                <td><Link href={`/device/${device.id}`}>{device?.name}</Link></td>
                                <td>{device?.type}</td>
                                <td>{device?.latitude}, {device?.longitude}</td>
                                <td>{device?.status}</td>
                                <td>{device?.last_seen_at}</td>
                                <td>{device?.user_id}</td>
                                <td><button className="edit">Edit</button></td>
                                <td><button className="delete">Delete</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>
            <section className={`admin-section ${activeTab === 'sensors' ? '' : 'invisible'}`}>
                <h2>Sensors</h2>
                <table className="admin-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Data type</th>
                            <th>Unit</th>
                            <th>Range</th>
                            <th>Device</th>
                            <th></th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {sensors.map(sensor => (
                            <tr key={sensor.id}>
                                <td><Link href={`/sensor/${sensor.id}`}>{sensor?.name}</Link></td>
                                <td>{sensor?.data_type}</td>
                                <td>{sensor?.unit}</td>
                                <td>{sensor.min_value} - {sensor.max_value}</td>
                                <td>{sensor.device_id}</td>
                                <td><button className="edit">Edit</button></td>
                                <td><button className="delete">Delete</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>
        </div>
    )
}

export default AdminPage;
