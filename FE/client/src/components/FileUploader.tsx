import { useState, useRef } from "react";
import { Upload, X } from "lucide-react";

interface FileUploaderProps {
  onFileChange: (file: File | null) => void;
  imagePreview: string | null;
}

export function FileUploader({ onFileChange, imagePreview }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files.length) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a valid image file (JPG, PNG, GIF)');
      return;
    }
    
    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size exceeds 5MB limit');
      return;
    }
    
    onFileChange(file);
  };

  const removeImage = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    onFileChange(null);
  };

  return (
    <div>
      {!imagePreview ? (
        <div 
          className={`
            border-2 border-dashed rounded-lg p-6 text-center cursor-pointer 
            ${isDragging ? 'border-purple-600' : 'border-gray-300 hover:border-purple-600'} 
            transition-colors
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="flex flex-col items-center justify-center">
            <Upload className="w-10 h-10 text-gray-400 mb-2" />
            <p className="text-purple-600 font-medium">Upload an image</p>
            <p className="text-gray-500 text-sm mt-1">PNG, JPG, GIF up to 5MB</p>
            <input 
              type="file" 
              ref={fileInputRef}
              className="hidden" 
              accept=".png,.jpg,.jpeg,.gif"
              onChange={handleFileSelect}
            />
          </div>
        </div>
      ) : (
        <div className="mt-3">
          <div className="relative">
            <img 
              className="w-full rounded-lg object-cover max-h-60" 
              src={imagePreview} 
              alt="Preview" 
            />
            <button 
              type="button" 
              className="absolute top-2 right-2 bg-white rounded-full p-1 shadow-md hover:bg-gray-100"
              onClick={removeImage}
            >
              <X className="w-5 h-5 text-gray-700" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
