import torch
import torchaudio
import numpy as np
from speechbrain.pretrained import EncoderClassifier
import os
import tempfile
import asyncio
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
import shutil

class VoiceAuthService:
    def __init__(self):
        # Load SpeechBrain ECAPA-TDNN model
        self.model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )
    
    def _resolve_ffmpeg(self) -> str:
        """Return path to an ffmpeg binary - system PATH first, then bundled."""
        sys_ffmpeg = shutil.which('ffmpeg')
        if sys_ffmpeg:
            return sys_ffmpeg
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as e:
            print(f"No ffmpeg available (system or bundled): {e}")
            return ""

    def _convert_to_wav(self, input_path: str, output_path: str) -> bool:
        """
        Convert audio file to WAV format using ffmpeg if available,
        otherwise use torchaudio
        """
        try:
            # Try using ffmpeg first (more reliable for various formats)
            ffmpeg_bin = self._resolve_ffmpeg()
            if ffmpeg_bin:
                result = subprocess.run([
                    ffmpeg_bin, '-i', input_path,
                    '-ar', '16000',  # Resample to 16kHz
                    '-ac', '1',       # Convert to mono
                    '-y',             # Overwrite output file
                    output_path
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    return True
                else:
                    print(f"FFmpeg conversion failed: {result.stderr}")
            
            # Fallback to torchaudio
            print("Attempting conversion with torchaudio...")
            signal, sr = torchaudio.load(input_path)
            
            # Convert to mono if stereo
            if signal.shape[0] > 1:
                signal = torch.mean(signal, dim=0, keepdim=True)
            
            # Resample to 16kHz if necessary
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(sr, 16000)
                signal = resampler(signal)
            
            # Save as WAV
            torchaudio.save(output_path, signal, 16000)
            return True
            
        except Exception as e:
            print(f"Audio conversion error: {e}")
            return False
    
    def extract_embedding(self, audio_data: bytes) -> np.ndarray:
        """Extract voice embedding from audio bytes"""
        # Determine file extension based on audio data
        # Try to detect format from first bytes
        if audio_data[:4] == b'RIFF':
            ext = '.wav'
        elif audio_data[:4] == b'OggS':
            ext = '.ogg'
        else:
            ext = '.webm'  # Default to webm for browser recordings
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(audio_data)
            tmp_input_path = tmp_file.name
        
        # Create temporary WAV file path
        tmp_wav_path = tmp_input_path.replace(ext, '_converted.wav')
        
        try:
            # Convert to WAV if not already
            if ext != '.wav':
                conversion_success = self._convert_to_wav(tmp_input_path, tmp_wav_path)
                if not conversion_success:
                    raise Exception("Failed to convert audio format")
                audio_path = tmp_wav_path
            else:
                audio_path = tmp_input_path
            
            # Load audio
            signal, sr = torchaudio.load(audio_path)
            
            # Convert to mono if stereo
            if signal.shape[0] > 1:
                signal = torch.mean(signal, dim=0, keepdim=True)
            
            # Resample if necessary (model expects 16kHz)
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(sr, 16000)
                signal = resampler(signal)
            
            # Extract embedding
            with torch.no_grad():
                embedding = self.model.encode_batch(signal)
                embedding = embedding.squeeze().cpu().numpy()
            
            return embedding
        
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            raise Exception(f"Voice embedding extraction failed: {str(e)}")
        
        finally:
            # Clean up temp files
            try:
                if os.path.exists(tmp_input_path):
                    os.unlink(tmp_input_path)
                if os.path.exists(tmp_wav_path):
                    os.unlink(tmp_wav_path)
            except:
                pass
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings"""
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        return float(similarity)
    
    async def extract_embedding_async(self, audio_data: bytes) -> np.ndarray:
        """Async wrapper that runs CPU-bound embedding extraction in a worker thread."""
        return await asyncio.to_thread(self.extract_embedding, audio_data)

    def get_audio_duration_seconds(self, audio_data: bytes) -> float:
        """Return audio duration in seconds; 0.0 if it cannot be decoded."""
        if audio_data[:4] == b'RIFF':
            ext = '.wav'
        elif audio_data[:4] == b'OggS':
            ext = '.ogg'
        else:
            ext = '.webm'

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(audio_data)
            tmp_input_path = tmp_file.name

        tmp_wav_path = tmp_input_path.replace(ext, '_dur.wav')
        try:
            audio_path = tmp_input_path
            if ext != '.wav':
                if not self._convert_to_wav(tmp_input_path, tmp_wav_path):
                    return 0.0
                audio_path = tmp_wav_path

            signal, sr = torchaudio.load(audio_path)
            return float(signal.shape[1]) / float(sr)
        except (RuntimeError, OSError) as e:
            print(f"Duration probe failed: {e}")
            return 0.0
        finally:
            for p in (tmp_input_path, tmp_wav_path):
                try:
                    if os.path.exists(p):
                        os.unlink(p)
                except OSError:
                    pass

    def embedding_to_string(self, embedding: np.ndarray) -> str:
        """Convert numpy array to comma-separated string for DB storage"""
        return ','.join(map(str, embedding.tolist()))
    
    def string_to_embedding(self, embedding_str: str) -> np.ndarray:
        """Convert comma-separated string back to numpy array"""
        return np.array([float(x) for x in embedding_str.split(',')])

# Singleton instance
voice_auth_service = VoiceAuthService()