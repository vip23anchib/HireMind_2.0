import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { BrainCircuit, Lock, User, AlertCircle, ArrowRight } from 'lucide-react';
import { Button } from '../../components/common/Button';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please provide both username and password.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await login({ username, password });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid username or password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-600 text-white shadow-lg shadow-indigo-500/30 mb-3">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">HireMind ATS</h1>
          <p className="text-slate-400 text-sm mt-1">Enterprise Recruitment Intelligence Portal</p>
        </div>

        {/* Login Box */}
        <div className="bg-white rounded-2xl p-8 shadow-2xl border border-slate-100">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-slate-800">Recruiter Sign In</h2>
            <p className="text-xs text-slate-500 mt-1">
              Enter your credentials to access the candidate management dashboard.
            </p>
          </div>

          {error && (
            <div className="mb-5 flex items-center gap-2.5 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Username or Email
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. recruiter or admin"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full mt-2"
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In to ATS
            </Button>
          </form>

          <div className="mt-6 pt-5 border-t border-slate-100 text-center">
            <a
              href="/careers"
              className="text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
            >
              &larr; Back to Public Careers Page
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
