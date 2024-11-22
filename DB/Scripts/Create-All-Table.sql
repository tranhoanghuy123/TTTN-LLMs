create database Project_TTTN;
use Project_TTTN
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) UNIQUE NOT NULL,
    password NVARCHAR(255) NOT NULL
);
CREATE TABLE uploaded_files (
    id INT IDENTITY(1,1) PRIMARY KEY,
    filename NVARCHAR(255) NOT NULL,
    file_data VARBINARY(MAX) NOT NULL,
    upload_time DATETIME DEFAULT GETDATE()
    UserId INT FOREIGN KEY REFERENCES users(id)
);

 

