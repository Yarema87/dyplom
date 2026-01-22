'use client';

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import Link from "next/link";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import EditDeviceForm from "../components/edit-device";
import EditSensorForm from "../components/edit-sensor";
import EditRuleForm from "../components/edit-rule";
import AddRuleForm from "../components/add-rule";

function AdminPage(){
    const [activeTab, setActiveTab] = useState('operators');
    const [user, setUser] = useState('');
    const [operators, setOperators] = useState([]);
    const [devices, setDevices] = useState([]);
    const [sensors, setSensors] = useState([]);
    const [sensorNames, setSensorNames] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [editDevice, setEditDevice] = useState(false);
    const [deviceToEdit, setDeviceToEdit] = useState('');
    const [editSensor, setEditSensor] = useState(false);
    const [sensorToEdit, setSensorToEdit] = useState('');
    const [addRule, setAddRule] = useState(false);
    const [editRule, setEditRule] = useState(false);
    const [ruleToEdit, setRuleToEdit] = useState('');
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
            setSensorNames(response.data.names);
        })
        .catch(error => {
            console.error('Error on fetching sensors:', error);
        })

        const rules_url = 'http://localhost:5000/api/rule/organization';
        axios.get(rules_url, {withCredentials: true})
        .then(response => {
            setAlerts(response.data.rules);
        })
        .catch(error => {
            console.error('Error on fetching alert rules:', error)
        })
    }, [])

    const approveUser = (user_id) => {
        const url = (`http://localhost:5000/api/admin/approve/${user_id}`);
        axios.patch(url)
        .then(response => {
            if(response.data.success){
                toast.success('User approved successfully');
            }
        })
        .catch(error => {
            console.error('Error on approving user:', error);
            toast.error('Something went wrong');
        })
    }

    const dismissUser = (user_id) => {
        const url = (`http://localhost:5000/api/admin/dismiss/${user_id}`);
        axios.patch(url)
        .then(response => {
            if(response.data.success){
                toast.success('User dismissed successfully');
            }
        })
        .catch(error => {
            console.error('Error on dismissing user:', error);
            toast.error('Something went wrong');
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

    const removeSensor = (sensor_id) => {
        const url = (`http://localhost:5000/api/sensors/remove/${sensor_id}`);
        axios.delete(url, {
        headers: {
                'Content-Type': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            if(response.data.success){
                toast.success('Sensor has been deleted');
            }
        })
        .catch(error => {
            toast.error('Something went wrong');
            console.error('Error on deleting sensor:', error);
        })
    }

    const removeRule = (rule_id) => {
        const url = (`http://localhost:5000/api/rule/remove/${rule_id}`);
        axios.delete(url, {
        headers: {
                'Content-Type': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            if(response.data.success){
                toast.success('Alert rule has been deleted');
            }
        })
        .catch(error => {
            toast.error('Something went wrong');
            console.error('Error on deleting alert rule:', error);
        })
    }

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
                                <td>
                                    <button 
                                    className="approve"
                                    onClick={() => !operator.status ? approveUser(operator.id) : dismissUser(operator.id)}>
                                        {operator.status ? 'Dismiss' : 'Approve'}
                                    </button>
                                </td>
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
                                <td>
                                    <button 
                                    className="edit"
                                    onClick={() => {
                                        setEditDevice(true);
                                        setDeviceToEdit(device.id);
                                    }}
                                    >
                                        Edit
                                    </button>
                                </td>
                                <td><button className="delete" onClick={() => removeDevice(device.id)}>Delete</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <EditDeviceForm visible={editDevice} setVisible={setEditDevice} device={deviceToEdit} operators={operators}/>
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
                                <td>
                                    <button 
                                    className="edit"
                                    onClick={() => {
                                        setEditSensor(true);
                                        setSensorToEdit(sensor.id);
                                    }}
                                    >
                                        Edit
                                    </button>
                                </td>
                                <td>
                                    <button 
                                    className="delete"
                                    onClick={() => removeSensor(sensor.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <EditSensorForm visible={editSensor} setVisible={setEditSensor} sensorId={sensorToEdit} devices={devices} />
            </section>
            <section className={`admin-section ${activeTab === 'alerts' ? '' : 'invisible'}`}>
                <h2>Alert rules</h2>
                <table className="admin-table">
                    <thead>
                    <tr>
                        <th>Sensor</th>
                        <th>Min value</th>
                        <th>Max value</th>
                        <th>Message</th>
                        <th>Status</th>
                        <th></th>
                        <th></th>
                    </tr>
                    </thead>
                    <tbody>
                        {alerts.map(rule => (
                            <tr key={rule.id}>
                                <td>
                                    {rule?.sensor_id ? rule.sensor_id : rule.sensor_name}
                                </td>
                                <td>
                                    {rule?.min_value ? rule.min_value : 'Min value is unset for this rule'}
                                </td>
                                <td>
                                    {rule?.max_value ? rule.max_value : 'Max value is unset for this rule'}
                                </td>
                                <td>{rule?.message}</td>
                                <td>{rule?.enabled ? 'Enabled' : 'Disabled'}</td>
                                <td>
                                    <button
                                    className="edit"
                                    onClick={() => {
                                        setEditRule(true);
                                        setRuleToEdit(rule.id);
                                    }}>
                                        Edit
                                    </button>
                                </td>
                                <td>
                                    <button
                                    className="delete"
                                    onClick={() => removeRule(rule.id)}>
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <button className="add-device-btn" onClick={() => setAddRule(true)}>
                    <span>+</span>
                    Add alert rule
                </button>
                <AddRuleForm visible={addRule} setVisible={setAddRule} sensors={sensors} names={sensorNames}/>
                <EditRuleForm visible={editRule} setVisible={setEditRule} rule_id={ruleToEdit} sensors={sensors} names={sensorNames}/>
            </section>
        </div>
    )
}

export default AdminPage;
