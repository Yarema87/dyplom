'use client';

import Link from "next/link";
import { useState, useEffect } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import axios from "axios";

function Header() {
    const [user, setUser] = useState('');
    const admin = user?.access === 'admin';
    const log_out = () => {
        const url = 'http://localhost:5000/api/user/logout';
        axios.post(url, {}, {
            headers: {
                'Content-Type': 'application/json'
            },
            withCredentials: true})
        .then(response => {
            setUser(null);
            toast.success('You have logged out successfully');
        })
        .catch(error => {
            console.error('Error on logging out:', error);
            toast.error('Something went wrong');
        })
    }

    useEffect(() => {
        const url = 'http://localhost:5000/api/auth';
        axios.get(url, {withCredentials: true})
        .then(response => {
            if(response.data.authenticated){
                setUser(response.data.user);
            }
            else{
                setUser(null);
            }
        })
    }, [])
    return(
        <header className="app-header">
            <Link href='/'>
                <div className="logo">
                    IoT Platform
                </div>
            </Link>
            {!user && (
                <nav>
                    <Link href='/login'>Log in</Link>
                    <Link href='/signup' className="primary">Sign up</Link>
                </nav>
            )}
            {user && !admin && (
                <nav>
                    <button onClick={() => log_out()}>Log out</button>
                </nav>
            )}
            {admin && (
                <nav>
                    <button onClick={() => log_out()}>Log out</button>
                    <Link href='/admin'>Admin</Link>
                </nav>
            )}
        </header>
    )
}

export default Header;