'use client';

import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from 'yup';
import axios from "axios";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useRouter } from "next/navigation";

function LogIn() {
    const router = useRouter();
    const login = async (values) => {
        try{
            const url = 'http://localhost:5000/api/user/login';
            const response = await axios.post(url, values, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            if(response.data.success) {
                toast.success("You have successfully logged in");
                router.push('/');
            }
        }
        catch(error) {
            if(error.response && error.response.status === 401){
                toast.error('Wrong email or password');
            }
            else if(error.response && error.response.status === 403){
                toast.error('Your admin has not approved you yet');
            }
            else if(error.response && error.response.status === 404){
                toast.error('You have not been registered yet');
            }
            else{
                toast.error('Some error occured');
                console.error('Error on loggin in:', error);
            }
        }
    }

    const validationSchema = Yup.object().shape({
        email: Yup.string()
            .required('Please, enter your email'),
        password: Yup.string()
            .required('Please, enter your password')
    });

    const googleLogin = () => {
        window.location.href = 'http://localhost:5000/api/user/google/login';
    };

    return(
        <div className="auth-page">
            <Formik
            initialValues={{
                email: '',
                password: '',
                remember: false
            }}
            onSubmit={login}
            validationSchema={validationSchema}>
                <Form className="auth-form">
                    <div>
                        <Field placeholder='Email' type='email' name='email' id='email' />
                        <ErrorMessage name='email' component='div' className="error_message" />
                    </div>
                    <div>
                        <Field placeholder='Password' type='password' name='password' id='password' />
                        <ErrorMessage name='password' component='div' className="error_message" />
                    </div>
                    <div className="checkbox-row">
                        <label>Remember me</label>
                        <Field type='checkbox' name='remember' id='remember' />
                    </div>
                    <button type="submit">Log in</button>
                    <button className="google-btn" onClick={() => googleLogin()}>
                        <span className="google-icon" />
                        <span className="google-text">Continue with Google</span>
                    </button>
                </Form>
            </Formik>
            
        </div>
    )
}

export default LogIn;