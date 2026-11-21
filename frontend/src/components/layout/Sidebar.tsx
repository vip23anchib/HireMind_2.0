import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  Users,
  GitBranch,
  Search,
  BarChart3,
  Clock,
  Sparkles,
} from 'lucide-react';
import { clsx } from 'clsx';

export const Sidebar: React.FC = () => {
  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Jobs', path: '/jobs', icon: Briefcase },
    { label: 'Candidates', path: '/candidates', icon: Users },
    { label: 'Pipeline', path: '/pipeline', icon: GitBranch },
    { label: 'ATS Search', path: '/search', icon: Search, badge: 'AI' },
    { label: 'Analytics', path: '/analytics', icon: BarChart3 },
    { label: 'Activity Log', path: '/activity', icon: Clock },
  ];

  return (
    <aside className="w-64 shrink-0 bg-white border-r border-slate-200/80 min-h-[calc(100vh-61px)] flex flex-col justify-between p-4">
      <div className="space-y-1">
        <p className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Recruitment Suite
        </p>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group',
                    isActive
                      ? 'bg-indigo-50/80 text-indigo-700 shadow-2xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  )
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 shrink-0 transition-colors group-hover:text-indigo-600" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-700 border border-indigo-200">
                    <Sparkles className="w-2.5 h-2.5" />
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
        <div className="flex items-center gap-2 mb-1.5">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <p className="text-xs font-semibold text-slate-700">Async Workers Active</p>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Celery & Redis queue operational for asynchronous OCR & skill indexing.
        </p>
      </div>
    </aside>
  );
};
