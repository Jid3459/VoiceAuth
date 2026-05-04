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
        # Anchor the model dir to this file's location so it works regardless
        # of the process cwd. A relative path here is fragile: if uvicorn is
        # launched from a different directory SpeechBrain silently re-creates
        # the cache, which can produce a slightly different embedding than
        # what was used at enrollment.
        model_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "pretrained_models",
            "spkrec-ecapa-voxceleb",
        )
        self.model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=model_dir,
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
    
    def _trim_silence(
        self,
        signal: torch.Tensor,
        sr: int = 16000,
        frame_ms: int = 30,
        threshold_db: float = -40.0,
    ) -> torch.Tensor:
        """Energy-based trim of leading/trailing silence. signal shape: [1, T].

        Browser webm recordings always contain ~100-500 ms of silence at
        each end (between clicking record/stop and actually speaking). On a
        2-3 s clip that silence dominates the embedding and tanks same-speaker
        similarity, so trim it before feeding ECAPA.
        """
        if signal.numel() == 0:
            return signal
        frame_len = int(sr * frame_ms / 1000)
        if frame_len <= 0 or signal.shape[1] < frame_len * 3:
            return signal
        x = signal[0]
        n_frames = x.shape[0] // frame_len
        frames = x[: n_frames * frame_len].reshape(n_frames, frame_len)
        rms = torch.sqrt(torch.mean(frames ** 2, dim=1) + 1e-12)
        peak = torch.max(rms).item()
        if peak <= 0:
            return signal
        threshold = peak * (10 ** (threshold_db / 20.0))
        voiced_idx = torch.nonzero(rms > threshold).flatten()
        if voiced_idx.numel() == 0:
            return signal
        start = int(voiced_idx[0].item()) * frame_len
        end = (int(voiced_idx[-1].item()) + 1) * frame_len
        trimmed = signal[:, start:end]
        # Safety: if trimming left less than 0.5 s, fall back to original.
        if trimmed.shape[1] < int(sr * 0.5):
            return signal
        return trimmed

    def _normalize_rms(self, signal: torch.Tensor, target_rms: float = 0.1) -> torch.Tensor:
        """Scale signal to a fixed RMS so browser auto-gain differences between
        enrollment and verification don't shift the embedding."""
        rms = torch.sqrt(torch.mean(signal ** 2) + 1e-12).item()
        if rms < 1e-6:
            return signal
        scaled = signal * (target_rms / rms)
        # Prevent clipping if a recording happens to be very quiet
        peak = torch.max(torch.abs(scaled)).item()
        if peak > 0.99:
            scaled = scaled * (0.99 / peak)
        return scaled

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

            # Symmetric preprocessing: silence trim + amplitude normalize.
            # Without this, same-speaker scores drop sharply because the
            # embedding is dominated by leading/trailing silence in browser
            # recordings and by inconsistent input gain.
            signal = self._trim_silence(signal, 16000)
            signal = self._normalize_rms(signal)

            # Extract embedding
            with torch.no_grad():
                embedding = self.model.encode_batch(signal)
                embedding = embedding.squeeze().cpu().numpy()

            # L2-normalize so the stored vector is on the unit sphere — makes
            # cosine similarity invariant to any incidental scaling the model
            # may apply, and keeps comparisons stable across versions.
            norm = float(np.linalg.norm(embedding))
            if norm > 1e-12:
                embedding = embedding / norm

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
        """Convert numpy array to comma-separated string for DB storage (legacy single-embedding format)."""
        return ','.join(map(str, embedding.tolist()))

    def string_to_embedding(self, embedding_str: str) -> np.ndarray:
        """Convert comma-separated string back to numpy array (legacy single-embedding format)."""
        return np.array([float(x) for x in embedding_str.split(',')])

    # ----- Multi-sample enrollment helpers -----
    # The User.voice_embedding text column stores a JSON list of "samples".
    # Each sample is a dict with id, name, created_at, and the embedding
    # vector. This lets a single user account hold multiple labeled voice
    # profiles — useful for both robustness (re-record yourself in different
    # mic conditions) and family accounts (multiple speakers per household).
    #
    # Two legacy formats are still readable for backwards compatibility:
    #   * a comma-separated single embedding (oldest)
    #   * a JSON list of plain arrays (intermediate, before sample metadata)

    def samples_to_string(self, samples) -> str:
        """Encode a list of sample-dicts as JSON for DB storage."""
        import json
        out = []
        for s in samples:
            out.append({
                "id": s["id"],
                "name": s.get("name") or "Sample",
                "created_at": s.get("created_at") or "",
                "embedding": s["embedding"].tolist() if hasattr(s["embedding"], "tolist") else list(s["embedding"]),
            })
        return json.dumps(out)

    def string_to_samples(self, stored: str):
        """Decode the stored samples blob into a list of sample-dicts.

        Returns [] for empty input. Handles both the new dict-of-metadata
        format and the two legacy formats (single comma-sep vector, or JSON
        list of plain arrays); legacy entries are auto-named "Sample 1", etc.
        """
        import json
        import uuid
        if not stored:
            return []
        stored = stored.strip()
        if not stored.startswith('['):
            # Legacy: single comma-separated vector
            arr = np.array([float(x) for x in stored.split(',')])
            return [{
                "id": str(uuid.uuid4()),
                "name": "Sample 1",
                "created_at": "",
                "embedding": arr,
            }]
        data = json.loads(stored)
        samples = []
        for i, item in enumerate(data):
            if isinstance(item, list):
                # Legacy: JSON list of plain arrays
                samples.append({
                    "id": str(uuid.uuid4()),
                    "name": f"Sample {i + 1}",
                    "created_at": "",
                    "embedding": np.array(item),
                })
            else:
                samples.append({
                    "id": item.get("id") or str(uuid.uuid4()),
                    "name": item.get("name") or f"Sample {i + 1}",
                    "created_at": item.get("created_at") or "",
                    "embedding": np.array(item["embedding"]),
                })
        return samples

    def compute_max_similarity_with_match(self, live: np.ndarray, samples):
        """Return (best_similarity, matched_sample_name) across all samples."""
        if not samples:
            return 0.0, None
        best_sim = -1.0
        best_name = None
        for s in samples:
            sim = self.compute_similarity(live, s["embedding"])
            if sim > best_sim:
                best_sim = sim
                best_name = s.get("name")
        return float(best_sim), best_name

    # --- Backwards-compatible thin wrappers used elsewhere in the codebase ---

    def embeddings_to_string(self, embeddings) -> str:
        """Legacy: list-of-arrays writer. Wraps each as an unnamed sample."""
        import uuid
        samples = [
            {"id": str(uuid.uuid4()), "name": f"Sample {i + 1}", "created_at": "", "embedding": e}
            for i, e in enumerate(embeddings)
        ]
        return self.samples_to_string(samples)

    def string_to_embeddings(self, stored: str):
        """Legacy: returns just the embedding arrays without metadata."""
        return [s["embedding"] for s in self.string_to_samples(stored)]

    def compute_max_similarity(self, live: np.ndarray, enrolled_list) -> float:
        """Legacy: returns just the best similarity number."""
        if not enrolled_list:
            return 0.0
        return max(self.compute_similarity(live, e) for e in enrolled_list)

# Singleton instance
voice_auth_service = VoiceAuthService()