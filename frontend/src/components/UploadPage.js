const handleUpload = async () => {
    if (!selectedFile) {
        setMessage('Please select a file first!');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        // Gửi file đến Flask API
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            setMessage(result.message);
        } else {
            setMessage(result.error || 'Failed to upload file.');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        setMessage('An error occurred while uploading.');
    }
};
