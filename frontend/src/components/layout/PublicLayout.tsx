import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { BrainCircuit, Lock } from 'lucide-react';

export const PublicLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <Link to="/careers" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-sm shadow-indigo-200">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight text-slate-900">
              HireMind Careers
            </span>
          </div>
        </Link>

        <Link
          to="/login"
          className="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold text-slate-600 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 border border-slate-200 rounded-lg transition-all"
        >
          <Lock className="w-3.5 h-3.5" />
          <span>Recruiter Sign In</span>
        </Link>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-10">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-400">
        <p>&copy; {new Date().getFullYear()} HireMind Enterprise ATS. Engineered for modern high-growth teams.</p>
      </footer>
    </div>
  );
};
