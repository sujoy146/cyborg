import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Toaster } from 'sonner';
import Background from './components/Background';
import NavBar from './components/NavBar';
import LandingPage from './pages/LandingPage';
import EncodePage from './pages/EncodePage';
import DecodePage from './pages/DecodePage';
import './App.css';

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export default function App() {
  // 'landing' | 'encode' | 'decode'
  const [view, setView] = useState('landing');

  const handleModeChange = (mode) => {
    setView(mode);
  };

  const handleLogoClick = () => {
    setView('landing');
  };

  return (
    <>
      <Background />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(12, 20, 40, 0.9)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(0, 229, 255, 0.15)',
            color: '#e2e8f0',
            fontFamily: "'Nunito Sans', sans-serif",
            fontSize: '0.875rem',
          },
        }}
        theme="dark"
      />

      {view !== 'landing' && (
        <NavBar
          mode={view}
          onModeChange={handleModeChange}
          onLogoClick={handleLogoClick}
        />
      )}

      <AnimatePresence mode="wait">
        {view === 'landing' && (
          <motion.div
            key="landing"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <LandingPage onSelectMode={handleModeChange} />
          </motion.div>
        )}

        {view === 'encode' && (
          <motion.div
            key="encode"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <EncodePage onBack={handleLogoClick} />
          </motion.div>
        )}

        {view === 'decode' && (
          <motion.div
            key="decode"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <DecodePage onBack={handleLogoClick} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
