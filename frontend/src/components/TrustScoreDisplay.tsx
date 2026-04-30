import React from 'react';
import { motion } from 'framer-motion';
import { Shield, TrendingUp, Activity, Smartphone, AlertTriangle, CheckCircle } from 'lucide-react';
import { TrustScores } from '../types';
import '../styles/TrustScoreDisplay.css';

interface TrustScoreDisplayProps {
  trustScores: TrustScores;
  overallScore: number;
  similarity: number;
}

const TrustScoreDisplay: React.FC<TrustScoreDisplayProps> = ({
  trustScores,
  overallScore,
  similarity,
}) => {
  const getScoreColor = (score: number): string => {
    if (score >= 85) return '#10b981';
    if (score >= 70) return '#3b82f6';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  const getSimilarityStatus = (sim: number): { text: string; color: string; icon: JSX.Element } => {
    if (sim >= 0.75) return { 
      text: 'Strong Match', 
      color: '#10b981',
      icon: <CheckCircle size={20} />
    };
    if (sim >= 0.50) return { 
      text: 'Uncertain', 
      color: '#f59e0b',
      icon: <AlertTriangle size={20} />
    };
    return { 
      text: 'No Match', 
      color: '#ef4444',
      icon: <AlertTriangle size={20} />
    };
  };

  const simStatus = getSimilarityStatus(similarity);

  const layerIcons: { [key: string]: JSX.Element } = {
    voice_biometrics: <Shield size={20} />,
    speech_consistency: <TrendingUp size={20} />,
    behavioral_pattern: <Activity size={20} />,
    device_integrity: <Smartphone size={20} />,
    contextual_anomaly: <AlertTriangle size={20} />
  };

  const layerNames: { [key: string]: string } = {
    voice_biometrics: 'Voice Biometrics',
    speech_consistency: 'Speech Consistency',
    behavioral_pattern: 'Behavioral Pattern',
    device_integrity: 'Device Integrity',
    contextual_anomaly: 'Contextual Anomaly'
  };

  return (
    <div className="trust-score-container">
      {/* Overall Score */}
      <motion.div 
        className="overall-score-card"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        <div className="score-circle-wrapper">
          <svg className="score-circle" viewBox="0 0 200 200">
            <circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="12"
            />
            <motion.circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              stroke={getScoreColor(overallScore)}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 90}`}
              strokeDashoffset={`${2 * Math.PI * 90 * (1 - overallScore / 100)}`}
              transform="rotate(-90 100 100)"
              initial={{ strokeDashoffset: 2 * Math.PI * 90 }}
              animate={{ strokeDashoffset: 2 * Math.PI * 90 * (1 - overallScore / 100) }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </svg>
          <div className="score-value">
            <span className="score-number" style={{ color: getScoreColor(overallScore) }}>
              {overallScore}
            </span>
            <span className="score-label">Trust Score</span>
          </div>
        </div>

        <div className="similarity-info" style={{ borderColor: simStatus.color }}>
          <div className="similarity-icon" style={{ color: simStatus.color }}>
            {simStatus.icon}
          </div>
          <div>
            <div className="similarity-value" style={{ color: simStatus.color }}>
              {(similarity * 100).toFixed(1)}%
            </div>
            <div className="similarity-status" style={{ color: simStatus.color }}>
              {simStatus.text}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Layer Scores */}
      <div className="layer-scores-grid">
        {Object.entries(trustScores).map(([key, value], index) => (
          <motion.div
            key={key}
            className="layer-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.3 }}
          >
            <div className="layer-header">
              <div className="layer-icon" style={{ color: getScoreColor(value) }}>
                {layerIcons[key]}
              </div>
              <span className="layer-name">{layerNames[key]}</span>
            </div>
            <div className="layer-score">
              <span className="layer-value" style={{ color: getScoreColor(value) }}>
                {value}
              </span>
              <div className="layer-bar">
                <motion.div
                  className="layer-bar-fill"
                  style={{ backgroundColor: getScoreColor(value) }}
                  initial={{ width: 0 }}
                  animate={{ width: `${value}%` }}
                  transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Score Legend */}
      <div className="score-legend">
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#10b981' }}></div>
          <span>Excellent (85-100)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#3b82f6' }}></div>
          <span>Good (70-84)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#f59e0b' }}></div>
          <span>Fair (50-69)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#ef4444' }}></div>
          <span>Poor (0-49)</span>
        </div>
      </div>
    </div>
  );
};

export default TrustScoreDisplay;