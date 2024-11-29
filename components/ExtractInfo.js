import React, { useState } from 'react';
import api from '../services/api';

const ExtractInfo = ({ selectedFile }) => {
    const [extractedData, setExtractedData] = useState(null);

    const extractData = async () => {
        try {
            const response = await api.post(`/extract/${selectedFile.id}`);
            setExtractedData(response.data.extracted_info);
        } catch (error) {
            console.error('Error extracting data:', error);
        }
    };

    return (
        <div className="extract-info">
            <h3>Extract Information</h3>
            {selectedFile ? (
                <>
                    <p>Selected File: {selectedFile.filename}</p>
                    <button onClick={extractData}>Extract Information</button>
                    {extractedData && (
                        <div className="extracted-data">
                            <h4>Extracted Data:</h4>
                            <pre>{JSON.stringify(extractedData, null, 2)}</pre>
                        </div>
                    )}
                </>
            ) : (
                <p>Please select a file to extract information</p>
            )}
        </div>
    );
};

export default ExtractInfo;
