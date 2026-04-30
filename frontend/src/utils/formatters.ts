/**
 * Utility functions for formatting data
 */

/**
 * Format currency in INR
 */
export const formatCurrency = (amount: number, locale: string = 'en-IN'): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format date and time
 */
export const formatDate = (
  dateString: string,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }
): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-IN', options).format(date);
};

/**
 * Format date only (no time)
 */
export const formatDateOnly = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

/**
 * Format time only
 */
export const formatTimeOnly = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) {
    return 'Just now';
  } else if (diffMin < 60) {
    return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
  } else if (diffHour < 24) {
    return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
  } else if (diffDay < 7) {
    return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
  } else {
    return formatDate(dateString);
  }
};

/**
 * Format percentage
 */
export const formatPercentage = (
  value: number,
  decimals: number = 1
): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format trust score with color
 */
export const getTrustScoreColor = (score: number): string => {
  if (score >= 85) return '#4caf50'; // Green
  if (score >= 70) return '#8bc34a'; // Light green
  if (score >= 50) return '#ff9800'; // Orange
  if (score >= 30) return '#ff5722'; // Deep orange
  return '#f44336'; // Red
};

/**
 * Format similarity score with status
 */
export const getSimilarityStatus = (
  similarity: number
): { text: string; color: string; emoji: string } => {
  if (similarity >= 0.75) {
    return { text: 'Strong Match', color: '#4caf50', emoji: '✓' };
  } else if (similarity >= 0.50) {
    return { text: 'Uncertain', color: '#ff9800', emoji: '⚠' };
  } else {
    return { text: 'No Match', color: '#f44336', emoji: '✗' };
  }
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Capitalize first letter
 */
export const capitalize = (text: string): string => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

/**
 * Convert snake_case to Title Case
 */
export const snakeToTitle = (text: string): string => {
  return text
    .split('_')
    .map((word) => capitalize(word))
    .join(' ');
};