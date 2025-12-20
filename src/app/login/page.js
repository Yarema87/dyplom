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
            toast.error('Some error occured');
            console.error('Error on loggin in:', error);
        }
    }
    return(
        <div>
            <Formik
            initialValues={{
                email: '',
                password: ''
            }}
            onSubmit={login}>
                <Form>
                    <div>
                        <Field placeholder='email' type='email' name='email' id='email' />
                    </div>
                    <div>
                        <Field placeholder='password' type='password' name='password' id='password' />
                    </div>
                    <button type="submit">Log in</button>
                </Form>
            </Formik>
        </div>
    )
}

export default LogIn;