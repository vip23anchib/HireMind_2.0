import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogOut, User as UserIcon, BrainCircuit, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-6 py-3.5 flex items-center justify-between shadow-2xs">
      <div className="flex items-center gap-4">
        <Link to="/dashboard" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-sm shadow-indigo-200 group-hover:scale-105 transition-transform">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-slate-900 to-indigo-950 bg-clip-text text-transparent">
              HireMind
            </span>
            <span className="text-xs ml-1.5 px-1.5 py-0.5 rounded font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200/60">
              PRO
            </span>
          </div>
        </Link>

        <div className="hidden sm:flex items-center gap-2 ml-4 pl-4 border-l border-slate-200">
          <Link
            to="/careers"
            target="_blank"
            className="flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-indigo-600 transition-colors"
          >
            <span>Live Careers Portal</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3 pr-2">
          <div className="w-8 h-8 rounded-full bg-indigo-100 border border-indigo-200 flex items-center justify-center text-indigo-700 font-bold text-xs">
            {user?.first_name ? user.first_name[0] : (user?.username?.[0]?.toUpperCase() || 'U')}
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-semibold text-slate-800 leading-tight">
              {user?.full_name || user?.username}
            </p>
            <p className="text-[11px] text-slate-500 leading-tight capitalize">
              {user?.role || 'Recruiter'}
            </p>
          </div>
        </div>

        <button
          onClick={logout}
          title="Sign out"
          className="p-2 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors border border-transparent hover:border-rose-100"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
