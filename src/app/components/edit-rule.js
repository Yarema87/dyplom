'use client';

import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from 'yup';
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function EditRuleForm({visible, setVisible, rule_id, sensors, names}) {
    const [user, setUser] = useState('');
    const [rule, setRule] = useState('');
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
        if (!rule_id) return;
        const url = (`http://localhost:5000/api/rule/${rule_id}`);
        axios.get(url)
        .then(response => {
            setRule(response.data.rule);
            console.log(response.data.rule);
        })
        .catch(error => {
            console.error('Error on fetching rule:', error)
        })
    }, [rule_id])

    const editRule = async (values) => {
        try{
            const url = (`http://localhost:5000/api/rule/edit/${rule_id}`);
            const response = await axios.patch(url, values, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            if (response.data.success){
                toast.success('Your alert rule has been edited');
                setVisible(false);
            }
        }
        catch (error){
            toast.error('Some error occured');
            console.error('Error on editing alert rule:', error);
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
                {rule && (
                    <Formik
                    initialValues={{
                        type: rule?.sensor_id ? 'id' : 'name',
                        sensor_id: rule?.sensor_id || '',
                        sensor_name: rule?.sensor_name || '',
                        min_value: rule?.min_value || '',
                        max_value: rule?.max_value || '',
                        message: rule?.message,
                        enabled: rule?.enabled
                    }}
                    onSubmit={values => editRule(values)}
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
                                    <Field as='select' name='sensor_name' id='sensor_name' >
                                        {names.map(name => (
                                            <option key={name.name} value={name.name}>
                                                {name.name}
                                            </option>
                                        ))}
                                    </Field>
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
                                <div>
                                    <label>Enabled</label>
                                    <Field type='checkbox' name='enabled' id='enabled' />
                                </div>
                                <button type='submit' disabled={!values.type}>Edit</button>
                            </Form>
                        )}
                    </Formik>
                )}
            </div>
        </div>
    )
}

export default EditRuleForm;
