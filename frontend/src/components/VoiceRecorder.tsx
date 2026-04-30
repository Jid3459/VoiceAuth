import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, AlertCircle } from 'lucide-react';
import '../styles/VoiceRecorder.css';

interface VoiceRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  isRecording: boolean;
  setIsRecording: (value: boolean) => void;
  minDuration?: number;
  maxDuration?: number;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onRecordingComplete,
  isRecording,
  setIsRecording,
  minDuration = 2,
  maxDuration = 30,
}) => {
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string>('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const analyserRef = useRef<Analyser | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (timerRef.current) clearInterval(timerRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    setError('');
    setRecordingTime(0);
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;

      // Setup audio level visualization
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateLevel = () => {
        if (isRecording) {
          analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average / 255 * 100);
          requestAnimationFrame(updateLevel);
        }
      };
      updateLevel();

      // Determine MIME type
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
        mimeType = 'audio/ogg;codecs=opus';
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 128000,
      });

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: mimeType });
        
        // Validate duration
        if (recordingTime < minDuration) {
          setError(`Recording must be at least ${minDuration} seconds`);
          return;
        }
        
        onRecordingComplete(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          
          // Auto-stop at max duration
          if (newTime >= maxDuration) {
            stopRecording();
          }
          
          return newTime;
        });
      }, 1000);

    } catch (error) {
      console.error('Microphone access error:', error);
      setError('Could not access microphone. Please grant permission.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = (): number => {
    return (recordingTime / maxDuration) * 100;
  };

  return (
    <div className="voice-recorder-container">
      <AnimatePresence mode="wait">
        {!isRecording ? (
          <motion.div
            key="start"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="recorder-idle"
          >
            <button onClick={startRecording} className="record-button start">
              <div className="button-content">
                <Mic size={32} />
                <span>Start Recording</span>
              </div>
            </button>
            <p className="recorder-hint">
              Click to start recording ({minDuration}-{maxDuration} seconds)
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="recording"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="recorder-active"
          >
            {/* Recording Indicator */}
            <div className="recording-status">
              <div className="recording-pulse"></div>
              <span>Recording...</span>
            </div>

            {/* Timer */}
            <div className="recording-timer">
              {formatTime(recordingTime)}
            </div>

            {/* Audio Level Visualizer */}
            <div className="audio-visualizer">
              {[...Array(20)].map((_, i) => (
                <motion.div
                  key={i}
                  className="visualizer-bar"
                  animate={{
                    height: `${Math.max(10, audioLevel * (0.5 + Math.random() * 0.5))}%`,
                  }}
                  transition={{
                    duration: 0.1,
                    ease: 'easeOut',
                  }}
                />
              ))}
            </div>

            {/* Progress Bar */}
            <div className="recording-progress">
              <div
                className="progress-bar"
                style={{ width: `${getProgressPercentage()}%` }}
              />
            </div>

            {/* Stop Button */}
            <button onClick={stopRecording} className="record-button stop">
              <div className="button-content">
                <Square size={32} />
                <span>Stop Recording</span>
              </div>
            </button>

            {/* Duration Warning */}
            {recordingTime < minDuration && (
              <div className="duration-warning">
                <AlertCircle size={16} />
                <span>Record for at least {minDuration} seconds</span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="recorder-error"
        >
          <AlertCircle size={20} />
          <span>{error}</span>
        </motion.div>
      )}
    </div>
  );
};

export default VoiceRecorder;