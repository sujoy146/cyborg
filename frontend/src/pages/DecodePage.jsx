import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import Stepper from '../components/Stepper';
import ImageUpload from '../components/ImageUpload';
import InputFields from '../components/InputFields';
import ResultView from '../components/ResultView';
import { DECODE_STEPS } from '../utils/constants';
import { decodeImage } from '../api/client';
import './EncodePage.css'; /* shared wizard styles */

const slideVariants = {
  enter: (dir) => ({ x: dir > 0 ? 200 : -200, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir) => ({ x: dir > 0 ? -200 : 200, opacity: 0 }),
};

export default function DecodePage({ onBack }) {
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [file, setFile] = useState(null);
  const [pin, setPin] = useState('');
  const [salt, setSalt] = useState('');
  const [inputsValid, setInputsValid] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const canNext = () => {
    if (step === 0) return !!file;
    if (step === 1) return inputsValid;
    return false;
  };

  const goNext = async () => {
    if (step === 1) {
      setDirection(1);
      setStep(2);
      setLoading(true);
      setError(null);
      try {
        const data = await decodeImage({
          stegoImage: file,
          pin,
          salt,
        });
        setResult(data);
      } catch (err) {
        setError(err.message);
        toast.error(err.message);
      } finally {
        setLoading(false);
      }
      return;
    }
    setDirection(1);
    setStep((s) => Math.min(s + 1, 2));
  };

  const goBack = () => {
    if (step === 0) {
      onBack();
      return;
    }
    setDirection(-1);
    setStep((s) => Math.max(s - 1, 0));
  };

  const handleStartOver = () => {
    setStep(0);
    setDirection(-1);
    setFile(null);
    setPin('');
    setSalt('');
    setResult(null);
    setError(null);
  };

  const handleRetry = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await decodeImage({
        stegoImage: file,
        pin,
        salt,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wizard-page">
      <Stepper steps={DECODE_STEPS} currentStep={step} />

      <div className="wizard-content">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={step}
            className="wizard-step-wrap"
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          >
            {step === 0 && (
              <ImageUpload file={file} onFileChange={setFile} />
            )}
            {step === 1 && (
              <InputFields
                mode="decode"
                message=""
                onMessageChange={() => {}}
                pin={pin}
                onPinChange={setPin}
                salt={salt}
                onSaltChange={setSalt}
                onValidChange={setInputsValid}
              />
            )}
            {step === 2 && (
              <ResultView
                mode="decode"
                loading={loading}
                error={error}
                result={result}
                onStartOver={handleStartOver}
                onRetry={handleRetry}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {step < 2 && (
        <div className="wizard-footer">
          <button className="btn btn-ghost" onClick={goBack}>
            <ArrowLeft size={14} /> Back
          </button>
          <button
            className="btn btn-primary"
            onClick={goNext}
            disabled={!canNext()}
          >
            {step === 1 ? 'Decode' : 'Next'} <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
