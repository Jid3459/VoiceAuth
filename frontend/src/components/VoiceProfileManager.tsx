import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Trash2, Plus, Users, Mic, Shield } from 'lucide-react';
import { toast } from 'react-toastify';
import VoiceRecorder from './VoiceRecorder';
import { authAPI } from '../services/api';

interface Sample {
  id: string;
  name: string;
  created_at: string;
}

interface Props {
  userId: number;
}

const formatDate = (iso: string): string => {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString();
};

const VoiceProfileManager: React.FC<Props> = ({ userId }) => {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [loading, setLoading] = useState(true);
  const [pendingName, setPendingName] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  const refresh = async () => {
    try {
      const data = await authAPI.listEnrollments(userId);
      setSamples(data.samples);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Could not load voice profiles');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const handleDelete = async (sample: Sample) => {
    if (!window.confirm(`Remove voice profile "${sample.name}"? This cannot be undone.`)) return;
    try {
      await authAPI.deleteEnrollmentSample(userId, sample.id);
      toast.success(`Deleted "${sample.name}"`);
      refresh();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to delete sample');
    }
  };

  const handleRecordingComplete = async (audioBlob: Blob) => {
    setIsUploading(true);
    try {
      const result = await authAPI.enrollVoice(userId, audioBlob, pendingName);
      toast.success(`Added "${result.sample_name}" (total: ${result.total_samples})`);
      setPendingName('');
      setShowAddForm(false);
      refresh();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to add voice sample');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: '24px' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'white', borderRadius: 12, padding: 24,
          boxShadow: '0 4px 12px rgba(0,0,0,0.05)', border: '1px solid #eef0f7',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <Users size={28} color="#5b6cf0" />
          <div>
            <h2 style={{ margin: 0 }}>Voice Profiles</h2>
            <p style={{ margin: 0, color: '#777', fontSize: 14 }}>
              Manage all enrolled voices on this account. Add multiple samples for yourself,
              or enroll family members under their own names.
            </p>
          </div>
        </div>

        <div style={{
          background: '#f4f7ff', border: '1px solid #cdd6f4',
          padding: '10px 14px', borderRadius: 8, fontSize: 13,
          color: '#444', margin: '14px 0 20px',
        }}>
          <Shield size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
          When you place an order, the system compares your live voice against
          <b> every</b> profile here and uses the best match. Any one of these
          voices can authenticate.
        </div>

        {loading ? (
          <p>Loading…</p>
        ) : samples.length === 0 ? (
          <div style={{
            border: '1px dashed #ccc', borderRadius: 8, padding: 24,
            textAlign: 'center', color: '#888',
          }}>
            <Mic size={32} style={{ opacity: 0.4 }} />
            <p>No voice profiles yet. Add your first sample below.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {samples.map((s) => (
              <div
                key={s.id}
                style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 16px', border: '1px solid #eef0f7', borderRadius: 8,
                  background: '#fafbff',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: 15 }}>{s.name}</div>
                  <div style={{ fontSize: 12, color: '#888' }}>
                    Enrolled {formatDate(s.created_at) || 'time unknown'}
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(s)}
                  title="Remove this sample"
                  style={{
                    background: 'none', border: '1px solid #f3c0c0', color: '#c0392b',
                    padding: '6px 10px', borderRadius: 6, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', gap: 6,
                  }}
                >
                  <Trash2 size={14} /> Remove
                </button>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: 24 }}>
          {!showAddForm ? (
            <button
              onClick={() => setShowAddForm(true)}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '10px 18px', background: '#5b6cf0', color: 'white',
                border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14,
              }}
            >
              <Plus size={16} /> Add Voice Profile
            </button>
          ) : (
            <div style={{
              border: '1px solid #cdd6f4', borderRadius: 10, padding: 18,
              background: '#fcfdff',
            }}>
              <h3 style={{ marginTop: 0, marginBottom: 8 }}>New voice sample</h3>
              <p style={{ color: '#666', fontSize: 13, marginTop: 0 }}>
                Give this sample a name (e.g. <i>"Mom"</i>, <i>"Dad"</i>, <i>"Office mic"</i>),
                then record at least 1.5 seconds of speech.
              </p>
              <input
                type="text"
                value={pendingName}
                onChange={(e) => setPendingName(e.target.value)}
                placeholder="e.g. Mom, Dad, Office mic"
                disabled={isRecording || isUploading}
                style={{
                  width: '100%', padding: '10px 12px', borderRadius: 6,
                  border: '1px solid #ccc', marginBottom: 12, fontSize: 14,
                }}
              />
              <VoiceRecorder
                onRecordingComplete={handleRecordingComplete}
                isRecording={isRecording}
                setIsRecording={setIsRecording}
              />
              {isUploading && (
                <p style={{ color: '#5b6cf0', marginTop: 8 }}>Uploading sample…</p>
              )}
              <button
                onClick={() => { setShowAddForm(false); setPendingName(''); }}
                disabled={isRecording || isUploading}
                style={{
                  marginTop: 12, padding: '8px 14px', background: 'transparent',
                  color: '#666', border: '1px solid #ddd', borderRadius: 6, cursor: 'pointer',
                }}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default VoiceProfileManager;
