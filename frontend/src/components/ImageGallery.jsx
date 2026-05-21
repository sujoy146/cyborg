import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Check, AlertCircle, Upload, Info } from 'lucide-react';
import { fetchGalleryImages } from '../api/client';
import { toast } from 'sonner';
import './ImageGallery.css';

export default function ImageGallery({ selected, onSelect, onFileUpload }) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasLoaded, setHasLoaded] = useState(false);
  const seenUrls = useRef(new Set());
  const [spinKey, setSpinKey] = useState(0);
  const [uploadPreview, setUploadPreview] = useState(null);
  const fileInputRef = useRef(null);

  const loadImages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const urls = await fetchGalleryImages();
      // Track seen URLs
      urls.forEach((u) => seenUrls.current.add(u));
      setImages(urls);
      setHasLoaded(true);
    } catch (err) {
      setError(err.message);
      toast.error('Failed to load images: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-load on first render
  if (!hasLoaded && !loading && !error) {
    loadImages();
  }

  const handleRefresh = () => {
    setSpinKey((k) => k + 1);
    onSelect(null);
    if (onFileUpload) onFileUpload(null);
    setUploadPreview(null);
    loadImages();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image too large. Max 10MB.');
      return;
    }

    // Create preview URL
    const previewUrl = URL.createObjectURL(file);
    setUploadPreview(previewUrl);
    onSelect(previewUrl);  // set as selected
    if (onFileUpload) onFileUpload(file);  // pass the actual File to parent
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleGallerySelect = (url) => {
    setUploadPreview(null);
    if (onFileUpload) onFileUpload(null);  // clear any uploaded file
    onSelect(url);
  };

  return (
    <div className="gallery">
      <div className="gallery-header">
        <div>
          <div className="gallery-title">Choose a Cover Image</div>
          <div className="gallery-subtitle">
            Select an image to hide your message in
          </div>
        </div>
        <div className="gallery-header-actions">
          <button
            className="gallery-upload-btn"
            onClick={handleUploadClick}
          >
            <Upload size={14} />
            Upload Your Own
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <button
            className="gallery-refresh"
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw
              size={14}
              key={spinKey}
              className={`gallery-refresh-icon ${loading ? 'spinning' : ''}`}
            />
            Refresh
          </button>
        </div>
      </div>

      <div className="gallery-grid">
        {/* Uploaded image preview */}
        {uploadPreview && (
          <motion.div
            className={`gallery-item ${selected === uploadPreview ? 'selected' : ''}`}
            onClick={() => handleGallerySelect(uploadPreview)}
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            layout
          >
            <img src={uploadPreview} alt="Your uploaded image" />
            <div className="gallery-upload-badge">Uploaded</div>
            {selected === uploadPreview && (
              <Check size={14} className="gallery-item-check" />
            )}
          </motion.div>
        )}

        {loading
          ? Array.from({ length: 9 }).map((_, i) => (
              <div key={`skel-${i}`} className="gallery-item skeleton-item">
                <div className="skeleton-inner" />
              </div>
            ))
          : error
            ? (
              <div className="gallery-error">
                <AlertCircle size={32} className="gallery-error-icon" />
                <p className="gallery-error-msg">{error}</p>
                <button className="btn btn-secondary" onClick={loadImages}>
                  Retry
                </button>
              </div>
            )
            : (
              <AnimatePresence mode="popLayout">
                {images.map((url, i) => (
                  <motion.div
                    key={url}
                    className={`gallery-item ${selected === url ? 'selected' : ''}`}
                    onClick={() => handleGallerySelect(url)}
                    initial={{ opacity: 0, scale: 0.85 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.85 }}
                    transition={{ duration: 0.35, delay: i * 0.04 }}
                    layout
                  >
                    <img src={url} alt={`Cover option ${i + 1}`} loading="lazy" />
                    {selected === url && (
                      <Check size={14} className="gallery-item-check" />
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
      </div>

      {/* Resize warning */}
      {selected && (
        <motion.div
          className="gallery-resize-warning"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Info size={13} />
          Image will be resized to 256×256 for encoding
        </motion.div>
      )}
    </div>
  );
}
