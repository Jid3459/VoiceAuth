import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium',
  color = 'currentColor'
}) => {
  return (
    <div 
      className={`loading-spinner ${size}`}
      style={{ borderTopColor: color }}
    />
  );
};

export default LoadingSpinner;