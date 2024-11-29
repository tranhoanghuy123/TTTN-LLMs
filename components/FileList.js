import React, { useEffect, useState } from 'react';
import api from '../services/api';

const FileList = ({ onSelectFile }) => {
    const [files, setFiles] = useState([]);

    useEffect(() => {
        const fetchFiles = async () => {
            try {
                const response = await api.get('/files');
                setFiles(response.data.files);
            } catch (error) {
                console.error('Error fetching files:', error);
            }
        };
        fetchFiles();
    }, []);

    return (
        <div className="file-list">
            <h3>Uploaded Files</h3>
            {files.length > 0 ? (
                <ul>
                    {files.map((file) => (
                        <li key={file.id} onClick={() => onSelectFile(file)}>
                            {file.filename}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No files available</p>
            )}
        </div>
    );
};

export default FileList;
