import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import ExtractInfo from './components/ExtractInfo';
import './App.css';

const App = () => {
    const [user, setUser] = useState(null); // Quản lý trạng thái người dùng
    const [selectedFile, setSelectedFile] = useState(null); // Quản lý trạng thái file được chọn

    const handleLogin = (userData) => {
        setUser(userData);
        localStorage.setItem('token', userData.token);
    };

    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('token');
    };

    return (
        <Router>
            <div className="app">
                <h1>Document Information Extraction</h1>
                <Routes>
                    {/* Route Đăng ký */}
                    <Route path="/register" element={<Register />} />
                    
                    {/* Route Đăng nhập */}
                    <Route
                        path="/login"
                        element={
                            user ? (
                                <Navigate to="/dashboard" />
                            ) : (
                                <Login onLogin={handleLogin} />
                            )
                        }
                    />
                    
                    {/* Route Dashboard */}
                    <Route
                        path="/dashboard"
                        element={
                            user ? (
                                <Dashboard onLogout={handleLogout}>
                                    {/* Dashboard hiển thị các tính năng */}
                                    <div className="dashboard-container">
                                        <FileUpload />
                                        <FileList onSelectFile={(file) => setSelectedFile(file)} />
                                        <ExtractInfo selectedFile={selectedFile} />
                                    </div>
                                </Dashboard>
                            ) : (
                                <Navigate to="/login" />
                            )
                        }
                    />
                    
                    {/* Redirect về Login nếu không có route phù hợp */}
                    <Route path="*" element={<Navigate to="/login" />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
