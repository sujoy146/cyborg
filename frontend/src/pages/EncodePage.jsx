import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import Stepper from '../components/Stepper';
import ImageGallery from '../components/ImageGallery';
import InputFields from '../components/InputFields';
import ResultView from '../components/ResultView';
import { ENCODE_STEPS } from '../utils/constants';
import { encodeImage } from '../api/client';
import './EncodePage.css';

const slideVariants = {
  enter: (dir) => ({ x: dir > 0 ? 200 : -200, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir) => ({ x: dir > 0 ? -200 : 200, opacity: 0 }),
};

export default function EncodePage({ onBack }) {
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);  // File object for uploads
  const [message, setMessage] = useState('');
  const [pin, setPin] = useState('');
  const [salt, setSalt] = useState('');
  const [inputsValid, setInputsValid] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const canNext = () => {
    if (step === 0) return !!selectedImage;
    if (step === 1) return inputsValid;
    return false;
  };

  const doEncode = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await encodeImage({
        imageUrl: uploadedFile ? null : selectedImage,
        imageFile: uploadedFile || null,
        message,
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

  const goNext = async () => {
    if (step === 1) {
      setDirection(1);
      setStep(2);
      await doEncode();
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
    setSelectedImage(null);
    setUploadedFile(null);
    setMessage('');
    setPin('');
    setSalt('');
    setResult(null);
    setError(null);
  };

  const handleRetry = async () => {
    await doEncode();
  };

  return (
    <div className="wizard-page">
      <Stepper steps={ENCODE_STEPS} currentStep={step} />

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
              <ImageGallery
                selected={selectedImage}
                onSelect={setSelectedImage}
                onFileUpload={setUploadedFile}
              />
            )}
            {step === 1 && (
              <InputFields
                mode="encode"
                message={message}
                onMessageChange={setMessage}
                pin={pin}
                onPinChange={setPin}
                salt={salt}
                onSaltChange={setSalt}
                selectedImage={selectedImage}
                onValidChange={setInputsValid}
              />
            )}
            {step === 2 && (
              <ResultView
                mode="encode"
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
            {step === 1 ? 'Encode' : 'Next'} <ArrowRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
