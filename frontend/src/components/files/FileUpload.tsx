import React, { useState } from 'react';
import { ingestAPI } from '../../services/api';

const FileUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['.pdf', '.docx', '.txt'];
    const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
    
    if (!validTypes.includes(fileExtension)) {
      setError('Please select a PDF, DOCX, or TXT file');
      return;
    }

    setUploading(true);
    setError('');
    setResult(null);

    try {
      const response = await ingestAPI.uploadFile(file);
      setResult(response.data);
      
      // Clear the file input
      e.target.value = '';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Documents</h3>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors duration-200">
        <input
          type="file"
          id="file-upload"
          className="hidden"
          onChange={handleFileUpload}
          accept=".pdf,.docx,.txt"
          disabled={uploading}
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer block"
        >
          <div className="flex flex-col items-center justify-center">
            <div className="text-4xl mb-4">📁</div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              {uploading ? 'Uploading...' : 'Choose a file to upload'}
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Supports PDF, DOCX, and TXT files
            </p>
            <div
              className={`px-6 py-3 rounded-lg font-medium ${
                uploading 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-primary-600 hover:bg-primary-700 cursor-pointer'
              } text-white transition-colors duration-200`}
            >
              {uploading ? 'Uploading...' : 'Select File'}
            </div>
          </div>
        </label>
      </div>

      {uploading && (
        <div className="mt-4 flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-sm text-gray-600">Processing your file...</span>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
          <p className="font-medium">Upload failed</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          <p className="font-medium">✅ Upload successful!</p>
          <p className="text-sm mt-1">
            Successfully processed {result.ingested_chunks} text chunks from your document.
          </p>
          {result.message && (
            <p className="text-sm mt-1">{result.message}</p>
          )}
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">How it works:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Upload documents to add them to your personal memory</li>
          <li>• The AI will extract and chunk the text content</li>
          <li>• Ask questions about your uploaded documents in the chat</li>
          <li>• Supported formats: PDF, Word documents (.docx), and text files</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;