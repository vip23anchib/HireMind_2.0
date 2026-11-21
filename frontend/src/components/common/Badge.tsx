import React from 'react';
import { clsx } from 'clsx';
import { ApplicationStatus } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple' | 'status';
  status?: ApplicationStatus | string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  status,
  size = 'md',
  className,
}) => {
  let badgeStyle = 'bg-slate-100 text-slate-700 border-slate-200';

  if (status) {
    switch (status) {
      case 'Applied':
        badgeStyle = 'bg-blue-50 text-blue-700 border-blue-200';
        break;
      case 'Under Review':
        badgeStyle = 'bg-amber-50 text-amber-700 border-amber-200';
        break;
      case 'Shortlisted':
        badgeStyle = 'bg-emerald-50 text-emerald-700 border-emerald-200';
        break;
      case 'Interview Scheduled':
      case 'Technical Assessment':
        badgeStyle = 'bg-purple-50 text-purple-700 border-purple-200';
        break;
      case 'Offer Extended':
      case 'Hired':
        badgeStyle = 'bg-teal-50 text-teal-800 border-teal-300 font-semibold';
        break;
      case 'Rejected':
        badgeStyle = 'bg-rose-50 text-rose-700 border-rose-200';
        break;
      default:
        badgeStyle = 'bg-slate-100 text-slate-700 border-slate-200';
    }
  } else {
    switch (variant) {
      case 'success':
        badgeStyle = 'bg-emerald-50 text-emerald-700 border-emerald-200';
        break;
      case 'warning':
        badgeStyle = 'bg-amber-50 text-amber-700 border-amber-200';
        break;
      case 'danger':
        badgeStyle = 'bg-rose-50 text-rose-700 border-rose-200';
        break;
      case 'info':
        badgeStyle = 'bg-blue-50 text-blue-700 border-blue-200';
        break;
      case 'purple':
        badgeStyle = 'bg-indigo-50 text-indigo-700 border-indigo-200';
        break;
      default:
        badgeStyle = 'bg-slate-100 text-slate-700 border-slate-200';
    }
  }

  const sizeStyle = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  }[size];

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 font-medium rounded-full border tracking-wide transition-colors',
        badgeStyle,
        sizeStyle,
        className
      )}
    >
      {children}
    </span>
  );
};
