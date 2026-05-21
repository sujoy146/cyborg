import { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, AlertTriangle } from 'lucide-react';
import { CHARSET } from '../utils/constants';
import { validateMessage, validatePin, validateSalt } from '../utils/validation';
import './InputFields.css';

export default function InputFields({
  mode = 'encode',
  message,
  onMessageChange,
  pin,
  onPinChange,
  salt,
  onSaltChange,
  selectedImage,
  onValidChange,
}) {
  const [showPin, setShowPin] = useState(false);
  const [showSalt, setShowSalt] = useState(false);
  const [touched, setTouched] = useState({});

  const msgVal = mode === 'encode' ? validateMessage(message) : { valid: true, errors: [], warnings: [] };
  const pinVal = validatePin(pin);
  const saltVal = validateSalt(salt);

  const allValid =
    mode === 'encode'
      ? msgVal.valid && pinVal.valid && saltVal.valid
      : pinVal.valid && saltVal.valid;

  // Notify parent of validity
  if (onValidChange) {
    onValidChange(allValid);
  }

  const handleBlur = (field) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  return (
    <div className="input-fields">
      <div className="input-fields-header">
        <div className="input-fields-title">
          {mode === 'encode' ? 'Message & Credentials' : 'Enter Credentials'}
        </div>
        <div className="input-fields-subtitle">
          {mode === 'encode'
            ? 'Type your secret message and enter keys shared with the receiver'
            : 'Enter the PIN and salt shared by the sender'}
        </div>
      </div>

      {/* Selected image preview (encode only) */}
      {mode === 'encode' && selectedImage && (
        <div className="selected-preview">
          <img src={selectedImage} alt="Selected cover" />
          <div className="selected-preview-info">
            <div className="selected-preview-label">Cover Image</div>
            <div className="selected-preview-name">Selected ✓</div>
          </div>
        </div>
      )}

      {/* Message input (encode only) */}
      {mode === 'encode' && (
        <motion.div
          className="input-group"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <label className="input-label">Secret Message</label>
          <input
            type="text"
            className={`input-field ${touched.message && !msgVal.valid ? 'error' : ''}`}
            placeholder="Enter the message you want to send"
            value={message}
            onChange={(e) => onMessageChange(e.target.value)}
            onBlur={() => handleBlur('message')}
          />
          <div>
              {touched.message && msgVal.errors.map((e, i) => (
                <div key={i} className="input-error">
                  <AlertTriangle size={12} /> {e}
                </div>
              ))}
              {msgVal.warnings.map((w, i) => (
                <div key={i} className="input-warning">
                  <AlertTriangle size={12} /> {w}
                </div>
              ))}
            </div>
        </motion.div>
      )}

      {/* PIN input */}
      <motion.div
        className="input-group"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: mode === 'encode' ? 0.2 : 0.1 }}
      >
        <label className="input-label">PIN</label>
        <div className="input-wrapper">
          <input
            type={showPin ? 'text' : 'password'}
            className={`input-field ${touched.pin && !pinVal.valid ? 'error' : ''}`}
            placeholder="Enter shared PIN"
            value={pin}
            onChange={(e) => onPinChange(e.target.value)}
            onBlur={() => handleBlur('pin')}
          />
          <button
            type="button"
            className="input-toggle"
            onClick={() => setShowPin(!showPin)}
            tabIndex={-1}
          >
            {showPin ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
        {touched.pin && pinVal.errors.map((e, i) => (
          <div key={i} className="input-error">
            <AlertTriangle size={12} /> {e}
          </div>
        ))}
      </motion.div>

      {/* Salt input */}
      <motion.div
        className="input-group"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: mode === 'encode' ? 0.3 : 0.2 }}
      >
        <label className="input-label">Salt</label>
        <div className="input-wrapper">
          <input
            type={showSalt ? 'text' : 'password'}
            className={`input-field ${touched.salt && !saltVal.valid ? 'error' : ''}`}
            placeholder="Enter shared salt"
            value={salt}
            onChange={(e) => onSaltChange(e.target.value)}
            onBlur={() => handleBlur('salt')}
          />
          <button
            type="button"
            className="input-toggle"
            onClick={() => setShowSalt(!showSalt)}
            tabIndex={-1}
          >
            {showSalt ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
        {touched.salt && saltVal.errors.map((e, i) => (
          <div key={i} className="input-error">
            <AlertTriangle size={12} /> {e}
          </div>
        ))}
      </motion.div>
    </div>
  );
}
