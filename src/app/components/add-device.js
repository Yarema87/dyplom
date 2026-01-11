'use client';

import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from 'yup';
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function AddDeviceForm({visible, setVisible}) {
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

    const addDevice = async (values) => {
        try{
            const url = 'http://localhost:5000/api/device/add';
            const response = await axios.post(url, values, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            if (response.data.success){
                toast.success('Your device has been added');
                setVisible(false);
            }
        }
        catch (error){
            toast.error('Some error occured');
            console.error('Error on adding device:', error);
        }
    }

    const validationSchema = Yup.object().shape({
        name: Yup.string()
        .required('Please, enter your device name'),
        type: Yup.string()
        .required('Please, enter your device type'),
        latitude: Yup.number()
        .required('Please, enter your device latitude')
        .typeError('Latitude should be a number'),
        longitude: Yup.number()
        .required('Please, enter your device longitude')
        .typeError('Longitude should be a number'),
        connection: Yup.string()
        .required('Please, enter your device ID')
    })

    return(
        <div className={`add-device-form ${visible ? '' : 'invisible'}`}>
            <Formik
            initialValues={{
                name: '',
                description: '',
                type: '',
                latitude: '',
                longitude: '',
                connection: ''
            }}
            validationSchema={validationSchema}
            onSubmit={addDevice}>
                <Form>
                    <div>
                        <Field placeholder='Device name' name='name' id='name' type='text' />
                        <ErrorMessage name='name' component='div' className="error_message" />
                    </div>
                    <div>
                        <Field placeholder='Description' name='description' id='description' as='textarea' />
                    </div>
                    <div>
                        <Field placeholder='Type' name='type' id='type' type='text' />
                        <ErrorMessage name='type' component='div' className="error_message" />
                    </div>
                    <div>
                        <label>Latitude</label>
                        <Field placeholder='24.1787' name='latitude' id='latitude' type='text' />
                        <ErrorMessage name='latitude' component='div' className="error_message" />
                    </div>
                    <div>
                        <label>Longitude</label>
                        <Field placeholder='24.1787' name='longitude' id='longitude' type='text' />
                        <ErrorMessage name='longitude' component='div' className="error_message" />
                    </div>
                    <div>
                        <label>Device Id</label>
                        <Field placeholder='My-device' name='connection' id='connection' type='text' />
                        <ErrorMessage name='connection' component='div' className="error_message" />
                    </div>
                    <button type='submit'>Add</button>
                </Form>
            </Formik>
        </div>
    )
}

export default AddDeviceForm;
