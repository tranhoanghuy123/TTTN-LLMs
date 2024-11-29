import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const isLoggedIn = !!localStorage.getItem('token');

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/'); // Quay lại trang Login
    };

    return (
        <nav className="navbar">
            <h1>Document Extraction App</h1>
            <div className="links">
                {isLoggedIn ? (
                    <>
                        <Link to="/dashboard">Dashboard</Link>
                        <Link to="/upload">Upload File</Link>
                        <Link to="/files">View Files</Link>
                        <button onClick={handleLogout}>Logout</button>
                    </>
                ) : (
                    <>
                        <Link to="/">Login</Link>
                        <Link to="/register">Register</Link>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
