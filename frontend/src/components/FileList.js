import React, { useEffect, useState } from 'react';

const FileList = () => {
    const [files, setFiles] = useState([]);

    useEffect(() => {
        // Lấy danh sách file từ Flask API
        fetch('http://localhost:5000/files')
            .then((res) => res.json())
            .then((data) => setFiles(data.files || []))
            .catch((err) => console.error('Error fetching files:', err));
    }, []);

    return (
        <div className="file-list">
            <h2>Uploaded Files</h2>
            <ul>
                {files.map((file, index) => (
                    <li key={index}>{file}</li>
                ))}
            </ul>
        </div>
    );
};

export default FileList;
