import React from 'react';
import { Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

interface AtsScoreBadgeProps {
  score: number;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const AtsScoreBadge: React.FC<AtsScoreBadgeProps> = ({
  score,
  showIcon = true,
  size = 'md',
}) => {
  const rounded = Math.round(score);

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';
  if (rounded >= 80) {
    colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-300 font-bold';
  } else if (rounded >= 60) {
    colorClasses = 'bg-blue-50 text-blue-700 border-blue-300 font-semibold';
  } else if (rounded >= 40) {
    colorClasses = 'bg-amber-50 text-amber-700 border-amber-300 font-medium';
  } else {
    colorClasses = 'bg-rose-50 text-rose-700 border-rose-300';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5',
  }[size];

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full border shadow-2xs transition-all',
        colorClasses,
        sizeClasses
      )}
      title={`ATS Match Score: ${rounded}%`}
    >
      {showIcon && <Sparkles className="w-3.5 h-3.5 shrink-0" />}
      <span>{rounded}% Match</span>
    </span>
  );
};
