'use client';

import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from 'yup';
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function EditDeviceForm({visible, setVisible, device, operators}) {
    const [user, setUser] = useState('');
    const [deviceData, setDeviceData] = useState('');
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
        if (!device) return;
        const url = (`http://localhost:5000/api/device/${device}`);
        axios.get(url)
        .then(response => {
            setDeviceData(response.data.device);
        })
        .catch(error => {
            console.error('Error on fetching device:', error);
        })
    }, [device])

    const editDevice = async (values) => {
        try{
            const url = (`http://localhost:5000/api/device/edit/${device}`);
            const response = await axios.patch(url, values, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            if (response.data.success){
                toast.success('Your device has been edited');
                setVisible(false);
            }
        }
        catch (error){
            toast.error('Some error occured');
            console.error('Error on editing device:', error);
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
        user: Yup.number()
        .required('Please, enter your device owner')
    })

    return(
        <div className={`add-device-form ${visible ? '' : 'invisible'}`} onClick={() => setVisible(false)}>
            <div onClick={(e) => e.stopPropagation()}>
                {deviceData && (
                    <Formik
                    initialValues={{
                        name: deviceData?.name,
                        description: deviceData?.description,
                        type: deviceData?.type,
                        latitude: deviceData?.latitude,
                        longitude: deviceData?.longitude,
                        user: deviceData?.user_id
                    }}
                    validationSchema={validationSchema}
                    onSubmit={editDevice}>
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
                                <Field name='longitude' id='longitude' type='text' />
                                <ErrorMessage name='longitude' component='div' className="error_message" />
                            </div>
                            <div>
                                <label>Owner</label>
                                <Field name='user' id='user' type='text' as='select'>
                                    {operators.map(operator => (
                                        <option key={operator.id} value={operator.id}>{operator?.name}</option>
                                    ))}
                                </Field>
                                <ErrorMessage name='user' component='div' className="error_message" />
                            </div>
                            <button type='submit'>Edit</button>
                        </Form>
                    </Formik>
                )}
            </div>
        </div>
    )
}

export default EditDeviceForm;
