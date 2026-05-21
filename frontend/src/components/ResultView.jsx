import { motion } from 'framer-motion';
import { Download, RotateCcw, AlertCircle, Sparkles, Lock } from 'lucide-react';
import './ResultView.css';

export default function ResultView({
  mode,
  loading,
  error,
  result,
  onStartOver,
  onRetry,
}) {
  // Loading state
  if (loading) {
    return (
      <div className="result-view">
        <div className="result-loading">
          <div className="result-spinner" />
          <div className="result-loading-text">
            {mode === 'encode' ? 'Encrypting & encoding your message…' : 'Extracting & decrypting the message…'}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="result-view">
        <div className="result-error">
          <AlertCircle size={40} className="result-error-icon" />
          <p className="result-error-msg">{error}</p>
          <div className="result-actions">
            <button className="btn btn-secondary" onClick={onRetry}>
              <RotateCcw size={14} /> Retry
            </button>
            <button className="btn btn-ghost" onClick={onStartOver}>
              Start Over
            </button>
          </div>
        </div>
      </div>
    );
  }

  // No result yet
  if (!result) return null;

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = result.stegoUrl;
    link.download = 'cyborg_stego.png';
    link.click();
  };

  // Encode result
  if (mode === 'encode') {
    return (
      <motion.div
        className="result-view"
        initial={{ opacity: 0, scale: 0.9, filter: 'blur(10px)' }}
        animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="result-header">
          <h2 className="result-title success">
            <Sparkles size={20} style={{ display: 'inline', marginRight: 8, verticalAlign: 'middle' }} />
            Encoding Complete
          </h2>
          <p className="result-subtitle">
            Your message is now hidden inside the image
          </p>
        </div>

        <div className="result-image-wrap">
          <img src={result.stegoUrl} alt="Stego image with hidden message" />
        </div>

        <div className="result-stats">
          <span className="badge badge-emerald">Format: PNG</span>
        </div>

        <div className="result-actions">
          <button className="btn btn-primary" onClick={handleDownload}>
            <Download size={16} /> Download Stego Image
          </button>
          <button className="btn btn-ghost" onClick={onStartOver}>
            <RotateCcw size={14} /> Encode Another
          </button>
        </div>
      </motion.div>
    );
  }

  // Decode result
  return (
    <motion.div
      className="result-view"
      initial={{ opacity: 0, scale: 0.9, filter: 'blur(10px)' }}
      animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="result-header">
        <h2 className="result-title success">
          <Sparkles size={20} style={{ display: 'inline', marginRight: 8, verticalAlign: 'middle' }} />
          Message Recovered
        </h2>
        <p className="result-subtitle">
          The hidden message has been successfully extracted
        </p>
      </div>

      <div className="result-message-box">
        <div className="result-message-label">Decoded Message</div>
        <motion.div
          className={`result-message-text ${result.message.length > 30 ? 'long' : result.message.length > 10 ? 'medium' : ''}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          {result.message}
        </motion.div>
      </div>



      <div className="result-actions">
        <button className="btn btn-primary" onClick={onStartOver}>
          <RotateCcw size={14} /> Decode Another
        </button>
      </div>
    </motion.div>
  );
}
