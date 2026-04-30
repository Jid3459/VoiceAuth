/**
 * Audio Utilities for Voice Recording and Processing
 */

export interface AudioConfig {
  sampleRate: number;
  channelCount: number;
  echoCancellation: boolean;
  noiseSuppression: boolean;
  autoGainControl: boolean;
}

const DEFAULT_AUDIO_CONFIG: AudioConfig = {
  sampleRate: 16000, // SpeechBrain expects 16kHz
  channelCount: 1, // Mono
  echoCancellation: true,
  noiseSuppression: true,
  autoGainControl: true,
};

/**
 * Request microphone permission and get audio stream
 */
export const getAudioStream = async (
  config: Partial<AudioConfig> = {}
): Promise<MediaStream> => {
  const audioConfig = { ...DEFAULT_AUDIO_CONFIG, ...config };

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: audioConfig.sampleRate,
        channelCount: audioConfig.channelCount,
        echoCancellation: audioConfig.echoCancellation,
        noiseSuppression: audioConfig.noiseSuppression,
        autoGainControl: audioConfig.autoGainControl,
      },
    });
    return stream;
  } catch (error) {
    console.error('Error accessing microphone:', error);
    throw new Error('Microphone access denied. Please grant permission.');
  }
};

/**
 * Stop all tracks in a media stream
 */
export const stopAudioStream = (stream: MediaStream): void => {
  stream.getTracks().forEach((track) => track.stop());
};

/**
 * Convert audio blob to WAV format
 */
export const convertToWav = async (audioBlob: Blob): Promise<Blob> => {
  // For simplicity, return as-is if already in supported format
  // In production, implement proper WAV conversion if needed
  return audioBlob;
};

/**
 * Get audio duration from blob
 */
export const getAudioDuration = (audioBlob: Blob): Promise<number> => {
  return new Promise((resolve, reject) => {
    const audio = new Audio();
    audio.preload = 'metadata';

    audio.onloadedmetadata = () => {
      resolve(audio.duration);
    };

    audio.onerror = () => {
      reject(new Error('Failed to load audio metadata'));
    };

    audio.src = URL.createObjectURL(audioBlob);
  });
};

/**
 * Validate audio blob meets minimum requirements
 */
export const validateAudioBlob = async (
  audioBlob: Blob,
  minDuration: number = 2, // minimum 2 seconds
  maxDuration: number = 30 // maximum 30 seconds
): Promise<{ valid: boolean; error?: string }> => {
  if (!audioBlob || audioBlob.size === 0) {
    return { valid: false, error: 'Audio blob is empty' };
  }

  try {
    const duration = await getAudioDuration(audioBlob);

    if (duration < minDuration) {
      return {
        valid: false,
        error: `Audio too short. Minimum ${minDuration} seconds required.`,
      };
    }

    if (duration > maxDuration) {
      return {
        valid: false,
        error: `Audio too long. Maximum ${maxDuration} seconds allowed.`,
      };
    }

    return { valid: true };
  } catch (error) {
    return { valid: false, error: 'Invalid audio format' };
  }
};

/**
 * Create audio visualizer
 */
export const createAudioVisualizer = (
  stream: MediaStream,
  canvas: HTMLCanvasElement
): (() => void) => {
  const audioContext = new AudioContext();
  const analyser = audioContext.createAnalyser();
  const source = audioContext.createMediaStreamSource(stream);
  source.connect(analyser);

  analyser.fftSize = 256;
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return () => {};
  }

  const draw = () => {
    requestAnimationFrame(draw);

    analyser.getByteFrequencyData(dataArray);

    ctx.fillStyle = 'rgb(240, 240, 240)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / bufferLength) * 2.5;
    let barHeight;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      barHeight = dataArray[i] / 2;

      const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
      gradient.addColorStop(0, '#667eea');
      gradient.addColorStop(1, '#764ba2');

      ctx.fillStyle = gradient;
      ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);

      x += barWidth + 1;
    }
  };

  draw();

  // Return cleanup function
  return () => {
    source.disconnect();
    audioContext.close();
  };
};

/**
 * Download audio blob as file
 */
export const downloadAudio = (audioBlob: Blob, filename: string = 'recording.wav'): void => {
  const url = URL.createObjectURL(audioBlob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  URL.revokeObjectURL(url);
  document.body.removeChild(a);
};