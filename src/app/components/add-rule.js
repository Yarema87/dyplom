'use client';

import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from 'yup';
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function AddRuleForm({visible, setVisible, sensors}) {
    const [user, setUser] = useState('');
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

    const addRule = async (values) => {
        try{
            const url = 'http://localhost:5000/api/rule/add';
            const response = await axios.post(url, values, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            if (response.data.success){
                toast.success('Your alert rule has been added');
                setVisible(false);
            }
        }
        catch (error){
            toast.error('Some error occured');
            console.error('Error on adding alert rule:', error);
        }
    }

    const validationSchema = Yup.object().shape({
        min_value: Yup.number()
        .typeError('Min value should be a number'),
        max_value: Yup.number()
        .typeError('Max value should be a number'),
        message: Yup.string()
        .required('Please, enter corresponding message')
    })

    return(
        <div className={`add-device-form ${visible ? '' : 'invisible'}`} onClick={() => setVisible(false)}>
            <div onClick={(e) => e.stopPropagation()}>
                <Formik
                initialValues={{
                    type: '',
                    sensor_id: '',
                    sensor_name: '',
                    min_value: '',
                    max_value: '',
                    message: '',
                }}
                onSubmit={values => addRule(values)}
                validationSchema={validationSchema}>
                    {({values}) => (
                        <Form>
                            <div>
                                <label>Select rule type</label>
                                <Field as='select' name='type' id='type'>
                                    <option value=''>Choose an option</option>
                                    <option value='id'>For single sensor</option>
                                    <option value='name'>For group of sensors</option>
                                </Field>
                            </div>
                            <div style={{display: `${values.type === 'id' ? 'flex' : 'none'}`}}>
                                <Field name='sensor_id' id='sensor_id' as='select'>
                                    {sensors.map(sensor => (
                                        <option key={sensor.id} value={sensor.id}>
                                            Sensor №{sensor.id} - {sensor.name}
                                        </option>
                                    ))}
                                </Field>
                            </div>
                            <div style={{display: `${values.type === 'name' ? 'flex' : 'none'}`}}>
                                <Field placeholder='Humidity sensor' name='sensor_name' id='sensor_name' />
                            </div>
                            <div>
                                <Field placeholder='Min value' name='min_value' id='min_value' type='text' />
                                <ErrorMessage name='min_value' component='div' className="error_message" />
                            </div>
                            <div>
                                <Field placeholder='Max value' name='max_value' id='max_value' type='text' />
                                <ErrorMessage name='max_value' component='div' className="error_message" />
                            </div>
                            <div>
                                <Field placeholder='Max value is exceded' name='message' id='message' as='textarea' />
                                <ErrorMessage name='message' component='div' className="error_message" />
                            </div>
                            <button type='submit' disabled={!values.type}>Add</button>
                        </Form>
                    )}
                </Formik>
            </div>
        </div>
    )
}

export default AddRuleForm;
