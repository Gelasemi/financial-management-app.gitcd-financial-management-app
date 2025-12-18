import React, { useState } from 'react';
import { Card, Upload, Button, message, Table, Tag, Progress } from 'antd';
import { InboxOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { uploadFile, getUploadedFiles } from '../services/api';

const { Dragger } = Upload;

const FileUpload = ({ onUploadSuccess }) => {
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleUpload = async (file) => {
    setUploading(true);
    setUploadProgress(0);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await uploadFile(formData, (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setUploadProgress(percentCompleted);
      });
      
      if (response.data.success) {
        message.success(`${file.name} uploaded successfully`);
        onUploadSuccess();
        fetchUploadedFiles();
      } else {
        message.error(`Failed to upload ${file.name}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      message.error(`Error uploading ${file.name}`);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const fetchUploadedFiles = async () => {
    try {
      const response = await getUploadedFiles();
      setUploadedFiles(response.data.files);
    } catch (error) {
      console.error('Error fetching uploaded files:', error);
    }
  };

  React.useEffect(() => {
    fetchUploadedFiles();
  }, []);

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    beforeUpload: (file) => {
      // Validate file type
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                     file.type === 'application/vnd.ms-excel';
      
      if (!isExcel) {
        message.error('You can only upload Excel files!');
        return false;
      }
      
      // Validate file size (max 10MB)
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('File must be smaller than 10MB!');
        return false;
      }
      
      // Start upload
      handleUpload(file);
      return false; // Prevent default upload behavior
    },
    fileList,
  };

  const columns = [
    {
      title: 'File Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Upload Date',
      dataIndex: 'uploadDate',
      key: 'uploadDate',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: status => (
        <Tag color={status === 'Processed' ? 'green' : 'orange'}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <div>
          <Button type="link" icon={<EyeOutlined />}>
            View
          </Button>
          <Button type="link" danger icon={<DeleteOutlined />}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="file-upload">
      <Card title="Upload Financial Report">
        <Dragger {...uploadProps} className="upload-area">
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Click or drag file to this area to upload</p>
          <p className="ant-upload-hint">
            Support for Excel files (.xlsx, .xls) only. Strictly prohibit from uploading company data or other
            band files
          </p>
        </Dragger>
        
        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Progress percent={uploadProgress} status="active" />
          </div>
        )}
        
        <div className="file-list">
          <h3>Uploaded Files</h3>
          <Table
            columns={columns}
            dataSource={uploadedFiles}
            rowKey="id"
            pagination={false}
          />
        </div>
      </Card>
    </div>
  );
};

export default FileUpload;