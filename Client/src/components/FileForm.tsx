import React, { useState, useRef } from "react";
import { Upload, X, File, CheckCircle } from "lucide-react";
import type { FileObjectType } from "@/types/fileType";
import { useUploadFile } from "@/hooks/useUpload";
import Loading from "./Loading";

export default function FileUpload({
  file,
  setFile,
}: {
  file: FileObjectType | null;
  setFile: React.Dispatch<React.SetStateAction<FileObjectType | null>>;
}) {
  const fileMutation = useUploadFile();
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
      addFile(droppedFiles[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files ?? []);
    if (selectedFiles.length > 0) {
      addFile(selectedFiles[0]);
    }
  };

  const addFile = (selectedFile: File) => {
    const fileObj = {
      id: crypto.randomUUID(),
      file: selectedFile,
      name: selectedFile.name,
      size: formatFileSize(selectedFile.size),
      uploaded: false,
    };
    setFile(fileObj);
  };

  const handleUpload = () => {
    if (!file) {
      alert("Please select a file to upload");
      return;
    }

    if (!file.uploaded) {
      fileMutation.mutate(file.file, {
        onSuccess: (response) => {
          alert(`File uploaded successfully!, File ID: ${response.fileId}`);
          setFile((prev) =>
            prev ? { ...prev, id: response.fileId, uploaded: true } : null
          );
        },
        onError: () => {
          alert("File upload failed. Please try again.");
        },
      });
    }
  };

  const removeFile = () => {
    setFile(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        {!fileMutation.isPending ? (
          <div className="bg-neutral-900 border border-neutral-800 rounded-lg shadow-xl p-8">
            <h2 className="text-3xl font-semibold text-neutral-50 mb-2">
              Upload Files
            </h2>
            <p className="text-neutral-400 mb-6">
              Drag and drop or click to select files
            </p>

            {/* Upload Area */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`
              border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
              transition-all duration-200 ease-in-out
              ${
                isDragging
                  ? "border-neutral-50 bg-neutral-800"
                  : "border-neutral-700 hover:border-neutral-600 hover:bg-neutral-800/50"
              }
            `}
            >
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                className="hidden"
              />

              <Upload
                className={`mx-auto mb-4 ${
                  isDragging ? "text-neutral-50" : "text-neutral-400"
                }`}
                size={48}
              />

              <p className="text-lg text-neutral-200 mb-2">
                {isDragging
                  ? "Drop files here"
                  : "Click to upload or drag and drop"}
              </p>
              <p className="text-sm text-neutral-500">
                Support for any file type
              </p>
            </div>

            {/* Upload Button */}
            {file && (
              <div className="mt-6">
                <button
                  onClick={handleUpload}
                  disabled={fileMutation.isPending}
                  className={`w-full font-semibold py-3 px-6 rounded-lg transition-colors duration-200 ${
                    file.uploaded
                      ? "bg-neutral-700 text-neutral-400 cursor-not-allowed"
                      : "bg-neutral-50 hover:bg-neutral-200 text-neutral-950"
                  }`}
                >
                  {file.uploaded ? "File Uploaded" : "Upload File"}
                </button>
              </div>
            )}

            {/* File Display */}
            {file && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-neutral-50 mb-4">
                  Selected File
                </h3>
                <div className="bg-neutral-800 border border-neutral-700 rounded-lg p-4 flex items-center justify-between hover:bg-neutral-800/80 transition-colors">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="flex-shrink-0">
                      {file.uploaded ? (
                        <CheckCircle className="text-green-500" size={24} />
                      ) : (
                        <File className="text-neutral-400" size={24} />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-neutral-50 font-medium truncate">
                        {file.name}
                      </p>
                      <p className="text-neutral-400 text-sm">{file.size}</p>
                    </div>
                  </div>
                  <button
                    onClick={removeFile}
                    className="flex-shrink-0 ml-4 p-2 hover:bg-neutral-700 rounded-lg transition-colors"
                  >
                    <X
                      className="text-neutral-400 hover:text-neutral-50"
                      size={20}
                    />
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <Loading />
        )}
      </div>
    </div>
  );
}
