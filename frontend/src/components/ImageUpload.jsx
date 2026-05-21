import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, X, Image } from 'lucide-react';
import { toast } from 'sonner';
import './ImageUpload.css';

const ACCEPTED_TYPES = ['image/png', 'image/jpeg', 'image/webp'];

export default function ImageUpload({ file, onFileChange }) {
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (f) => {
    if (!f) return;
    if (!ACCEPTED_TYPES.includes(f.type)) {
      toast.error('Unsupported format. Use PNG, JPG, or WEBP.');
      return;
    }
    if (f.size > 20 * 1024 * 1024) {
      toast.error('File too large. Max 20MB.');
      return;
    }
    onFileChange(f);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    handleFile(f);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleClear = () => {
    onFileChange(null);
    setPreview(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  if (file && preview) {
    return (
      <motion.div
        className="upload-preview"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="upload-zone-header">
          <div className="upload-zone-title">Stego Image Ready</div>
          <div className="upload-zone-subtitle">This image will be decoded</div>
        </div>
        <div className="upload-preview-img-wrap">
          <img src={preview} alt="Uploaded stego" />
        </div>
        <p className="upload-preview-name">{file.name}</p>
        <div className="upload-preview-change">
          <button className="btn btn-ghost" onClick={handleClear}>
            <X size={14} /> Change Image
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="upload-zone">
      <div className="upload-zone-header">
        <div className="upload-zone-title">Upload Stego Image</div>
        <div className="upload-zone-subtitle">
          Upload the image you received from the sender
        </div>
      </div>
      <motion.div
        className={`upload-dropzone ${dragOver ? 'drag-over' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <Image size={40} className="upload-icon" />
        <div className="upload-text">
          <p className="upload-text-main">
            Drag & drop or <span>browse</span>
          </p>
          <p className="upload-text-sub">PNG, JPG, WEBP — Max 20MB</p>
        </div>
      </motion.div>
      <input
        ref={inputRef}
        type="file"
        accept=".png,.jpg,.jpeg,.webp"
        onChange={(e) => handleFile(e.target.files[0])}
      />
    </div>
  );
}
