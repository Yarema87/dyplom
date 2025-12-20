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

    return(
        <div>
            <Formik
            initialValues={{
                name: '',
                email: '',
                password: '',
                organization: ''
            }}
            onSubmit={register}
            >
                <Form>
                    <div>
                        <Field placeholder='name' name='name' id='name' />
                    </div>
                    <div>
                        <Field placeholder='organisation' name='organization' id='organization' />
                    </div>
                    <div>
                        <Field placeholder='email' type='email' name='email' id='email' />
                    </div>
                    <div>
                        <Field placeholder='password' type='password' name='password' id='password' />
                    </div>
                    <button type="submit">Sign up</button>
                </Form>
            </Formik>
        </div>
    )
}

export default SignUp;