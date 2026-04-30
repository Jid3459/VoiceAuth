import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mic, Check, AlertCircle, Loader } from 'lucide-react';
import { toast } from 'react-toastify';
import VoiceRecorder from './VoiceRecorder';
import { authAPI } from '../services/api';
import '../styles/VoiceEnrollment.css';

interface VoiceEnrollmentProps {
  userId: number;
  onEnrollmentComplete: () => void;
}

const VoiceEnrollment: React.FC<VoiceEnrollmentProps> = ({
  userId,
  onEnrollmentComplete,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingStep, setRecordingStep] = useState(0);
  const [recordings, setRecordings] = useState<Blob[]>([]);

  const steps = [
    {
      title: "First Recording",
      instruction: "Please say: 'My voice is my password'",
      duration: "5-10 seconds"
    },
    {
      title: "Second Recording",
      instruction: "Please say: 'I authorize this device'",
      duration: "5-10 seconds"
    },
    {
      title: "Final Recording",
      instruction: "Please say: 'Security is my priority'",
      duration: "5-10 seconds"
    }
  ];

  const handleRecordingComplete = async (audioBlob: Blob) => {
    const newRecordings = [...recordings, audioBlob];
    setRecordings(newRecordings);

    if (recordingStep < steps.length - 1) {
      setRecordingStep(recordingStep + 1);
      toast.success(`Recording ${recordingStep + 1} completed!`);
    } else {
      // All recordings complete, enroll voice
      await enrollVoice(newRecordings[0]); // Using first recording for enrollment
    }
  };

  const enrollVoice = async (audioBlob: Blob) => {
    setIsProcessing(true);
    try {
      await authAPI.enrollVoice(userId, audioBlob);
      toast.success('🎉 Voice enrolled successfully!');
      setTimeout(() => {
        onEnrollmentComplete();
      }, 1500);
    } catch (error: any) {
      console.error('Enrollment error:', error);
      toast.error(error.response?.data?.detail || 'Enrollment failed. Please try again.');
      // Reset on error
      setRecordings([]);
      setRecordingStep(0);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetEnrollment = () => {
    setRecordings([]);
    setRecordingStep(0);
    setIsRecording(false);
    setIsProcessing(false);
  };

  return (
    <div className="voice-enrollment-container">
      <motion.div 
        className="enrollment-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="enrollment-header">
          <div className="enrollment-icon">
            <Mic size={32} />
          </div>
          <h2>Voice Enrollment</h2>
          <p>Secure your account with voice biometric authentication</p>
        </div>

        {/* Progress Steps */}
        <div className="enrollment-progress">
          {steps.map((step, index) => (
            <div 
              key={index}
              className={`progress-step ${index === recordingStep ? 'active' : ''} ${index < recordingStep ? 'completed' : ''}`}
            >
              <div className="step-number">
                {index < recordingStep ? <Check size={16} /> : index + 1}
              </div>
              <span className="step-label">{step.title}</span>
            </div>
          ))}
        </div>

        {!isProcessing ? (
          <>
            {/* Current Step Info */}
            <div className="step-info">
              <h3>{steps[recordingStep].title}</h3>
              <div className="instruction-box">
                <AlertCircle size={20} />
                <p>{steps[recordingStep].instruction}</p>
              </div>
              <div className="duration-info">
                <span>Duration: {steps[recordingStep].duration}</span>
              </div>
            </div>

            {/* Voice Recorder */}
            <div className="recorder-section">
              <VoiceRecorder
                onRecordingComplete={handleRecordingComplete}
                isRecording={isRecording}
                setIsRecording={setIsRecording}
              />
            </div>

            {/* Tips */}
            <div className="enrollment-tips">
              <h4>📌 Tips for Best Results:</h4>
              <ul>
                <li>Find a quiet environment</li>
                <li>Speak clearly and naturally</li>
                <li>Keep consistent distance from microphone</li>
                <li>Record for the full duration</li>
              </ul>
            </div>

            {/* Reset Button */}
            {recordings.length > 0 && (
              <button 
                onClick={resetEnrollment}
                className="btn btn-secondary"
                disabled={isRecording}
              >
                Start Over
              </button>
            )}
          </>
        ) : (
          <div className="processing-state">
            <Loader className="processing-spinner" size={48} />
            <h3>Processing Your Voice...</h3>
            <p>Creating your unique voice signature</p>
          </div>
        )}

        {/* Security Info */}
        <div className="security-info">
          <div className="security-badge">
            <Check size={16} />
            <span>Your voice data is encrypted and never stored as audio</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default VoiceEnrollment;