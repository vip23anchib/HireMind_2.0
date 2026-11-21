import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { resumesApi } from '../../api/resumes';
import { DocumentRecord } from '../../types';

interface ResumeUploaderProps {
  candidateId?: number;
  jobId?: number;
  onSuccess?: (doc: DocumentRecord) => void;
  className?: string;
}

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  candidateId,
  jobId,
  onSuccess,
  className = '',
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusText, setStatusText] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const validateAndSelectFile = (selectedFile: File) => {
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setErrorMessage('Only PDF documents are supported.');
      return false;
    }
    if (selectedFile.size > 5 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 5MB limit.');
      return false;
    }
    setErrorMessage(null);
    setFile(selectedFile);
    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const pollDocumentStatus = async (docId: number) => {
    setStatusText('Processing resume intelligence...');
    let attempts = 0;
    const maxAttempts = 30; // 30 * 1000ms = 30 seconds

    const interval = setInterval(async () => {
      attempts++;
      try {
        const doc = await resumesApi.getResumeStatus(docId);
        if (doc.status === 'Completed') {
          clearInterval(interval);
          setUploadStatus('success');
          setStatusText('Resume parsed & skills indexed successfully!');
          if (onSuccess) onSuccess(doc);
        } else if (doc.status === 'Failed') {
          clearInterval(interval);
          setUploadStatus('error');
          setErrorMessage(doc.error_message || 'Resume parsing failed. Please check document quality.');
        } else if (attempts >= maxAttempts) {
          clearInterval(interval);
          setUploadStatus('success'); // Still uploaded, background worker will finish
          setStatusText('Resume queued. Skills will sync shortly.');
        }
      } catch (err) {
        clearInterval(interval);
        setUploadStatus('error');
        setErrorMessage('Failed to check resume processing status.');
      }
    }, 1000);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadStatus('uploading');
    setStatusText('Uploading resume to server...');
    setErrorMessage(null);

    try {
      const response = await resumesApi.uploadResume(file, candidateId, jobId);
      setUploadStatus('processing');
      await pollDocumentStatus(response.id);
    } catch (err: any) {
      setUploadStatus('error');
      setErrorMessage(err.message || 'Failed to upload resume.');
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]'
            : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center gap-2">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800">
              {file ? file.name : 'Click or drag & drop candidate resume'}
            </p>
            <p className="text-xs text-slate-500 mt-1">PDF format only, maximum 5MB</p>
          </div>
        </div>
      </div>

      {file && uploadStatus === 'idle' && (
        <div className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-lg">
          <div className="flex items-center gap-2.5">
            <FileText className="w-5 h-5 text-indigo-600" />
            <span className="text-sm font-medium text-slate-700 truncate max-w-xs">{file.name}</span>
            <span className="text-xs text-slate-400">({(file.size / 1024).toFixed(1)} KB)</span>
          </div>
          <button
            type="button"
            onClick={handleUpload}
            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
          >
            Upload & Analyze
          </button>
        </div>
      )}

      {(uploadStatus === 'uploading' || uploadStatus === 'processing') && (
        <div className="flex items-center gap-3 p-3.5 bg-indigo-50/70 border border-indigo-100 rounded-lg text-indigo-700 text-sm">
          <Loader2 className="w-4 h-4 animate-spin shrink-0 text-indigo-600" />
          <span>{statusText}</span>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="flex items-center gap-3 p-3.5 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-sm">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{statusText}</span>
        </div>
      )}

      {(uploadStatus === 'error' || errorMessage) && (
        <div className="flex items-center gap-3 p-3.5 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
