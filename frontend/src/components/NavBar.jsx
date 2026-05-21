import { useRef, useEffect, useState } from 'react';
import { Shield } from 'lucide-react';
import './NavBar.css';

export default function NavBar({ mode, onModeChange, onLogoClick }) {
  const encodeRef = useRef(null);
  const decodeRef = useRef(null);
  const [sliderStyle, setSliderStyle] = useState({});

  useEffect(() => {
    const activeBtn = mode === 'encode' ? encodeRef.current : decodeRef.current;
    if (activeBtn) {
      setSliderStyle({
        left: activeBtn.offsetLeft + 'px',
        width: activeBtn.offsetWidth + 'px',
      });
    }
  }, [mode]);

  return (
    <nav className="navbar">
      <div className="navbar-brand" onClick={onLogoClick}>
        <Shield className="navbar-logo-icon" />
        <span className="navbar-logo">CYBORG</span>
      </div>

      <div className="navbar-toggle">
        <div className="navbar-toggle-slider" style={sliderStyle} />
        <button
          ref={encodeRef}
          className={`navbar-toggle-btn ${mode === 'encode' ? 'active' : ''}`}
          onClick={() => onModeChange('encode')}
        >
          Encode
        </button>
        <button
          ref={decodeRef}
          className={`navbar-toggle-btn ${mode === 'decode' ? 'active' : ''}`}
          onClick={() => onModeChange('decode')}
        >
          Decode
        </button>
      </div>
    </nav>
  );
}
