'use client';

import { Formik, Form, Field, ErrorMessage } from "formik";
import { useState, useEffect } from "react";
import * as Yup from 'yup';
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function EditSensorForm({visible, setVisible, sensorId, devices}) {
    const [sensor, setSensor] = useState('');

    useEffect(() => {
        if (!sensorId) return;
        const url = (`http://localhost:5000/api/sensors/${sensorId}`);
        axios.get(url)
        .then(response => {
            setSensor(response.data.sensor);
        })
        .catch(error => {
            console.error('Error on fetching sensor:', error);
        })
    }, [sensorId])
    
    const editSensor = async (values) => {
        try{
            const url = (`http://localhost:5000/api/sensors/edit/${sensorId}`);
            const response = await axios.patch(url, values, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            if (response.data.success){
                toast.success('Your sensor has been edited');
                setVisible(false);
            }
        }
        catch (error){
            toast.error('Some error occured');
            console.error('Error on editing sensor:', error);
        }
    }

    const validationSchema = Yup.object().shape({
        name: Yup.string()
        .required('Please, enter your sensor name'),
        unit: Yup.string()
        .required('Please, enter your sensor measurement unit'),
        data_type: Yup.string()
        .required('Please, enter your sensor data type'),
        min_value: Yup.number()
        .typeError('Min value should be a number'),
        max_value: Yup.number()
        .typeError('Max value should be a number'),
        device_id: Yup.number()
        .required('Please, choose your sensor device'),
    })

    return(
        <div className={`add-device-form ${visible ? '' : 'invisible'}`} onClick={() => setVisible(false)}>
            <div onClick={(e) => e.stopPropagation()}>
                {sensor && (
                    <Formik
                    initialValues={{
                        name: sensor?.name,
                        unit: sensor?.unit,
                        data_type: sensor?.data_type,
                        max_value: sensor?.max_value,
                        min_value: sensor?.min_value,
                        device_id: sensor?.device_id
                    }}
                    validationSchema={validationSchema}
                    onSubmit={editSensor}
                    >
                        <Form>
                            <div>
                                <Field name='name' id='name' type='text' />
                                <ErrorMessage name='name' component='div' className="error_message" />
                            </div>
                            <div>
                                <Field name='unit' id='unit' type='text' />
                                <ErrorMessage name='unit' component='div' className="error_message" />
                            </div>
                            <div>
                                <Field name='data_type' id='data_type' as='select' >
                                    <option value='Int'>Int</option>
                                    <option value='Float'>Float</option>
                                    <option value='Boolean'>Boolean</option>
                                    <option value='String'>String</option>
                                </Field>
                                <ErrorMessage name='data_type' component='div' className="error_message" />
                            </div>
                            <div>
                                <Field name='min_value' id='min_value' type='text' />
                                <ErrorMessage name='min_value' component='div' className="error_message" />
                            </div>
                            <div>
                                <Field name='max_value' id='max_value' type='text' />
                                <ErrorMessage name='max_value' component='div' className="error_message" />
                            </div>
                            <div>
                                <Field name='device_id' id='device_id' as='select'>
                                    {devices.map(device => (
                                        <option key={device.id} value={device.id}>{device.name}</option>
                                    ))}
                                </Field>
                            </div>
                            <button type='submit'>Edit</button>
                        </Form>
                    </Formik>
                )}
            </div>
        </div>
    )
}

export default EditSensorForm;
