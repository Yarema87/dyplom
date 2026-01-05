'use client';

import { useState, useEffect } from "react";
import axios from "axios";
import Statistics from "@/app/components/sensor-chart";

function SensorPage({params}){
    const [sensor, setSensor] = useState('');

    useEffect(() => {
        async function fetchParams() {
            const sensorId = await params;
            const sensor_url = (`http://localhost:5000/api/sensors/${decodeURIComponent(sensorId.sensorId)}`);
            axios.get(sensor_url)
            .then(response => {
                setSensor(response.data.sensor);
            })
            .catch(error => {
                console.error('Error on fetching sensor:', error);
            })
        }
        fetchParams();
    }, [params])

    return(
        <div className="device-page">
            <div className="device-page-card">
                <h1 className="device-title">{sensor.name}</h1>
                <div className="device-meta">
                    <p>
                        <span>Units:</span>
                        <span>{sensor.unit}</span>
                    </p>
                    <p>
                        <span>Data type:</span>
                        <span>{sensor.data_type}</span>
                    </p>
                    <p>
                        <span>Measurements range:</span>
                        {sensor.min_value}{sensor.unit} - {sensor.max_value}{sensor.unit}
                    </p>
                </div>
                <Statistics sensor_id={sensor.id}/>
            </div>
        </div>
    )
}

export default SensorPage;