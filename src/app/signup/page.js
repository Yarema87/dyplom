'use client';

import { useRouter } from "next/navigation";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from 'yup';
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function SignUp(){
    const router = useRouter();
    const register = async (values) => {
        try{
            const url = 'http://localhost:5000/api/user/sign-up';
            const response = await axios.post(url, values, {
                headers: {
                    'Content-Type': 'application/json'
                }
                // withCredentials: true  // Only if you need cookies/sessions
            });
            if(response.data.success) {
                toast.success("You have successfully registered");
                router.push('/');
            }
        }
        catch(error) {
            toast.error('Some error occured');
            console.error('Error on registering:', error);
        }
    }

    const validationSchema = Yup.object().shape({
        name: Yup.string()
            .required('Please, enter your name'),
        email: Yup.string()
            .required('Please, enter your email')
            .email('Wrong format of email'),
        organization: Yup.string()
            .required('Please, enter your organization'),
        password: Yup.string()
            .required('Please, enter your password')
            .min(8, 'Password must be at least 8 characters long'),
        confirm_password: Yup.string()
            .required('Please, confirm your password')
            .oneOf([Yup.ref('password'), null], 'Passwords must match')
    })

    return(
        <div className="auth-page">
            <Formik
            initialValues={{
                name: '',
                email: '',
                password: '',
                confirm_password: '',
                organization: ''
            }}
            onSubmit={register}
            validationSchema={validationSchema}
            >
                <Form className="auth-form">
                    <div>
                        <Field placeholder='Name' type='text' name='name' id='name' />
                        <ErrorMessage name='name' component='div' className="error_message" />
                    </div>
                    <div>
                        <Field placeholder='Organisation' type='text' name='organization' id='organization' />
                        <ErrorMessage name='organization' component='div' className="error_message" />
                    </div>
                    <div>
                        <Field placeholder='Email' type='email' name='email' id='email' />
                        <ErrorMessage name='email' component='div' className="error_message" />
                    </div>
                    <div>
                        <Field placeholder='Password' type='password' name='password' id='password' />
                        <ErrorMessage name='password' component='div' className="error_message" />
                    </div>
                    <div>
                        <Field placeholder='Confirm password' type='password' name='confirm_password' id='confirm_password' />
                        <ErrorMessage name='confirm_password' component='div' className="error_message" />
                    </div>
                    <button type="submit">Sign up</button>
                </Form>
            </Formik>
        </div>
    )
}

export default SignUp;