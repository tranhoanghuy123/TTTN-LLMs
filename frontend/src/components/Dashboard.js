import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
    return (
        <div className="dashboard">
            <h1>Dashboard</h1>
            <p>Welcome to the Document Extraction App Dashboard!</p>
            <div className="dashboard-links">
                <Link to="/upload" className="btn">Upload File</Link>
                <Link to="/files" className="btn">View Uploaded Files</Link>
            </div>
        </div>
    );
};

export default Dashboard;
