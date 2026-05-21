import { Check } from 'lucide-react';
import './Stepper.css';

export default function Stepper({ steps, currentStep }) {
  return (
    <div className="stepper">
      {steps.map((step, i) => {
        const isCompleted = i < currentStep;
        const isActive = i === currentStep;

        return (
          <div key={i} className="stepper-item">
            <div
              className={`stepper-circle ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
            >
              {isCompleted ? <Check size={16} /> : i + 1}
            </div>
            <div className="stepper-info">
              <span
                className={`stepper-label ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
              >
                {step.label}
              </span>
              <span className="stepper-desc">{step.description}</span>
            </div>
            {i < steps.length - 1 && (
              <div className="stepper-connector">
                <div
                  className={`stepper-connector-fill ${isCompleted ? 'filled' : ''}`}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
