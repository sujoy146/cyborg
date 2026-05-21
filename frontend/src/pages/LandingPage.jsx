import { motion } from 'framer-motion';
import { Lock, Unlock } from 'lucide-react';
import { CHARSET } from '../utils/constants';
import './LandingPage.css';

export default function LandingPage({ onSelectMode }) {
  return (
    <div className="landing">
      <motion.div
        className="landing-hero"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      >
        <h1 className="landing-title">CYBORG</h1>
        <p className="landing-subtitle">
          A Covert Message Transfer Platform.
        </p>
      </motion.div>

      <div className="landing-cards">
        <motion.div
          className="landing-card landing-card--encode"
          onClick={() => onSelectMode('encode')}
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="landing-card-icon">
            <Lock size={24} />
          </div>
          <h3 className="landing-card-title">Encode</h3>
          <p className="landing-card-desc">
            Hide a secret message inside a cover image to send to someone
          </p>
        </motion.div>

        <motion.div
          className="landing-card landing-card--decode"
          onClick={() => onSelectMode('decode')}
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="landing-card-icon">
            <Unlock size={24} />
          </div>
          <h3 className="landing-card-title">Decode</h3>
          <p className="landing-card-desc">
            Extract a hidden message from a stego image you received
          </p>
        </motion.div>
      </div>

      <motion.div
        className="landing-footer"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <span className="landing-charset">
          Charset: {CHARSET}
        </span>
      </motion.div>
    </div>
  );
}
