import React, { useEffect, useState } from 'react';
import { orderAPI } from '../services/api';
import { AuthLog } from '../types';
import { formatDate } from '../utils/formatters';
import '../styles/AuthLogs.css';

interface AuthLogsProps {
  userId: number;
}

const AuthLogs: React.FC<AuthLogsProps> = ({ userId }) => {
  const [logs, setLogs] = useState<AuthLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadLogs();
  }, [userId]);

  const loadLogs = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await orderAPI.getAuthLogs(userId, 20);
      setLogs(data);
    } catch (err) {
      setError('Failed to load authentication logs');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const getDecisionColor = (decision: string) => {
    return decision === 'ALLOW' ? '#4caf50' : '#f44336';
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.75) return '#4caf50';
    if (similarity >= 0.50) return '#ff9800';
    return '#f44336';
  };

  if (isLoading) {
    return <div className="auth-logs-loading">Loading authentication logs...</div>;
  }

  if (error) {
    return (
      <div className="auth-logs-error">
        <p>{error}</p>
        <button onClick={loadLogs}>Retry</button>
      </div>
    );
  }

  return (
    <div className="auth-logs">
      <div className="auth-logs-header">
        <h2>Authentication History</h2>
        <button onClick={loadLogs} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      {logs.length === 0 ? (
        <div className="no-logs">No authentication logs yet</div>
      ) : (
        <div className="logs-table-container">
          <table className="logs-table">
            <thead>
              <tr>
                <th>Date & Time</th>
                <th>Action</th>
                <th>Similarity</th>
                <th>Trust Score</th>
                <th>Decision</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{formatDate(log.created_at)}</td>
                  <td className="action-cell">{log.action_attempted}</td>
                  <td>
                    <span
                      className="similarity-badge"
                      style={{ backgroundColor: getSimilarityColor(log.speechbrain_similarity) }}
                    >
                      {(log.speechbrain_similarity * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td>
                    <div className="trust-score-cell">
                      <div className="score-number">{log.overall_trust_score}</div>
                      <div className="score-bar">
                        <div
                          className="score-bar-fill"
                          style={{
                            width: `${log.overall_trust_score}%`,
                            backgroundColor: log.overall_trust_score >= 70 ? '#4caf50' : '#ff9800'
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td>
                    <span
                      className="decision-badge"
                      style={{ backgroundColor: getDecisionColor(log.decision) }}
                    >
                      {log.decision}
                    </span>
                  </td>
                  <td>
                    <button
                      className="details-btn"
                      onClick={() => alert(JSON.stringify(log.trust_scores, null, 2))}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AuthLogs;