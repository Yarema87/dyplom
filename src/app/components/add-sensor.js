'use client';

import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from 'yup';
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function AddSensorForm({visible, setVisible, deviceId}) {
    
    const addSensor = async (values) => {
        try{
            const url = 'http://localhost:5000/api/sensors/add';
            const payload = {
                ...values,
                device_id: deviceId,
            }
            const response = await axios.post(url, payload, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            if (response.data.success){
                toast.success('Your sensor has been added');
                setVisible(false);
            }
        }
        catch (error){
            toast.error('Some error occured');
            console.error('Error on adding sensor:', error);
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
    })

    return(
        <div className={`add-device-form ${visible ? '' : 'invisible'}`} onClick={() => setVisible(false)}>
            <div onClick={(e) => e.stopPropagation()}>
                <Formik
                initialValues={{
                    name: '',
                    unit: '',
                    data_type: '',
                    max_value: '',
                    min_value: '',
                }}
                validationSchema={validationSchema}
                onSubmit={addSensor}
                >
                    <Form>
                        <div>
                            <Field placeholder='Sensor name' name='name' id='name' type='text' />
                            <ErrorMessage name='name' component='div' className="error_message" />
                        </div>
                        <div>
                            <Field placeholder='Unit' name='unit' id='unit' type='text' />
                            <ErrorMessage name='unit' component='div' className="error_message" />
                        </div>
                        <div>
                            <Field placeholder='Data type' name='data_type' id='data_type' as='select' >
                                <option value='Int'>Int</option>
                                <option value='Float'>Float</option>
                                <option value='Boolean'>Boolean</option>
                                <option value='String'>String</option>
                            </Field>
                            <ErrorMessage name='data_type' component='div' className="error_message" />
                        </div>
                        <div>
                            <Field placeholder='Min value' name='min_value' id='min_value' type='text' />
                            <ErrorMessage name='min_value' component='div' className="error_message" />
                        </div>
                        <div>
                            <Field placeholder='Max value' name='max_value' id='max_value' type='text' />
                            <ErrorMessage name='max_value' component='div' className="error_message" />
                        </div>
                        <button type='submit'>Add</button>
                    </Form>
                </Formik>
            </div>
        </div>
    )
}

export default AddSensorForm;
