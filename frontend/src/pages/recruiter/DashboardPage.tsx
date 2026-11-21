import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Briefcase,
  UserCheck,
  TrendingUp,
  Plus,
  Search,
  UploadCloud,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { analyticsApi } from '../../api/analytics';
import { applicationsApi } from '../../api/applications';
import { DashboardMetrics, Application } from '../../types';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { AtsScoreBadge } from '../../components/resume/AtsScoreBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentApplications, setRecentApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashData, appsRes] = await Promise.all([
          analyticsApi.getDashboardSummary(),
          applicationsApi.getApplications({ page: 1 }),
        ]);
        setMetrics(dashData);
        setRecentApplications(appsRes.results.slice(0, 6));
      } catch (err) {
        console.error('Failed to load dashboard metrics', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Loading recruitment intelligence dashboard..." size="lg" />;
  }

  const statCards = [
    {
      label: 'Active Candidates',
      value: metrics?.total_candidates ?? 0,
      icon: Users,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
    {
      label: 'Open Jobs',
      value: metrics?.active_jobs ?? 0,
      icon: Briefcase,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Shortlisted & Interviewing',
      value: metrics?.shortlisted_candidates ?? 0,
      icon: Sparkles,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
    },
    {
      label: 'Hired Candidates',
      value: metrics?.hired_candidates ?? 0,
      icon: UserCheck,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 p-8 rounded-2xl text-white shadow-md">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-indigo-200 text-xs font-medium mb-3 backdrop-blur-xs">
            <TrendingUp className="w-3.5 h-3.5 text-indigo-300" />
            <span>Recruitment Performance Overview</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">HireMind ATS Command Center</h1>
          <p className="text-indigo-200/80 text-sm mt-1 max-w-xl">
            Live pipeline analytics, candidate scoring, and automated resume processing powered by Celery & Redis.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          <Link
            to="/jobs"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-white text-indigo-900 rounded-xl font-semibold text-xs shadow-sm hover:bg-indigo-50 transition-all active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>Post New Job</span>
          </Link>
          <Link
            to="/search"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium text-xs backdrop-blur-xs border border-white/20 transition-all"
          >
            <Search className="w-4 h-4" />
            <span>ATS Candidate Search</span>
          </Link>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {statCards.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <Card key={idx} className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {stat.label}
                  </p>
                  <p className="text-3xl font-extrabold text-slate-900 mt-2 font-mono">
                    {stat.value}
                  </p>
                </div>
                <div className={`w-12 h-12 rounded-xl ${stat.bgColor} flex items-center justify-center ${stat.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Recent Applications & Pipeline Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Applications Table */}
        <Card className="lg:col-span-2 p-6">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Recent Applications</h2>
              <p className="text-xs text-slate-500">Live candidate submissions & ATS match ratings</p>
            </div>
            <Link
              to="/pipeline"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
            >
              <span>View Full Pipeline</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-slate-400 text-xs uppercase tracking-wider border-b border-slate-100">
                  <th className="pb-3 font-semibold">Candidate</th>
                  <th className="pb-3 font-semibold">Applied Role</th>
                  <th className="pb-3 font-semibold">ATS Score</th>
                  <th className="pb-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentApplications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 pr-4">
                      <p className="font-semibold text-slate-800">{app.candidate_name}</p>
                      <p className="text-xs text-slate-400">{app.candidate_email}</p>
                    </td>
                    <td className="py-3.5 pr-4">
                      <span className="font-medium text-slate-700">{app.job_title}</span>
                    </td>
                    <td className="py-3.5 pr-4">
                      <AtsScoreBadge score={app.ats_score} size="sm" />
                    </td>
                    <td className="py-3.5">
                      <Badge status={app.status}>{app.status}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Pipeline Distribution Summary */}
        <Card className="p-6 flex flex-col justify-between">
          <div>
            <div className="mb-6 pb-4 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-900">Pipeline Funnel</h2>
              <p className="text-xs text-slate-500">Candidate distribution by stage</p>
            </div>

            <div className="space-y-4">
              {metrics?.pipeline_breakdown &&
                Object.entries(metrics.pipeline_breakdown).map(([stage, count]) => {
                  const total = metrics.total_applications || 1;
                  const pct = Math.round((count / total) * 100);
                  return (
                    <div key={stage} className="space-y-1.5">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-slate-700">{stage}</span>
                        <span className="text-slate-500 font-mono font-semibold">
                          {count} ({pct}%)
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${Math.max(pct, 4)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>

          <div className="mt-8 pt-4 border-t border-slate-100">
            <Link
              to="/analytics"
              className="w-full flex items-center justify-center gap-2 py-2.5 text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-xl transition-colors"
            >
              <span>Explore Advanced Analytics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
