'use client';

import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import debounce from "lodash.debounce";

function Statistics({sensor_id}){
    const [telemetry, setTelemetry] = useState([]);
    const [sensor, setSensor] = useState('');
    const [days, setDays] = useState(1);

    const fetchProgress = useCallback(debounce((sensor_id, days) => {
        const url = (`http://localhost:5000/api/telemetry/${sensor_id}/${days}`);
        axios.get(url)
        .then(response => {
            setTelemetry(response.data.telemetry);
            console.log(response.data.telemetry);
        })
        .catch(error => {
            console.error('Error on getting telemetry:', error);
        })
    }, 500), []);

    useEffect(() => {
        fetchProgress(sensor_id, days);
    }, [sensor_id, days, fetchProgress])

    useEffect(() => {
        if (!sensor_id) return;
        const url = (`http://localhost:5000/api/sensors/${sensor_id}`);
        axios.get(url)
        .then(response => {
            setSensor(response.data.sensor);
        })
        .catch(error => {
            console.error('Error on fetching sensor:', error);
        })
    }, [sensor_id])

    const chartData = telemetry.map(t => ({
        ...t,
        time: new Date(t.timestamp).toLocaleTimeString()
    }));


    return(
        <div>
            {sensor && (
                <div>
                    <ResponsiveContainer width='100%' height={400}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey='time' />
                            <YAxis label={{value: sensor.unit, angle: -90, position: 'insideLeft'}} />
                            <Tooltip />
                            <Line type='monotone' dataKey='value' stroke="#8884d8" strokeWidth={3} />
                        </LineChart>
                    </ResponsiveContainer>
                    <label>Days:</label>
                    <input 
                    type='range'
                    id='days'
                    name='days'
                    min='1'
                    max='30'
                    onChange={(e) => setDays(e.target.value)}/>
                </div>
            )}
        </div>
    )
}

export default Statistics;