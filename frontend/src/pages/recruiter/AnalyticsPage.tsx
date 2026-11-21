import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart,
  Users,
  Award,
  Sparkles,
} from 'lucide-react';
import { analyticsApi } from '../../api/analytics';
import {
  DashboardMetrics,
  SkillDistributionItem,
  ExperienceDistributionItem,
  FunnelStage,
} from '../../types';
import { Card } from '../../components/common/Card';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const AnalyticsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [skills, setSkills] = useState<SkillDistributionItem[]>([]);
  const [experience, setExperience] = useState<ExperienceDistributionItem[]>([]);
  const [funnel, setFunnel] = useState<FunnelStage[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [dash, sk, exp, fn] = await Promise.all([
          analyticsApi.getDashboardSummary(),
          analyticsApi.getSkillsDistribution(),
          analyticsApi.getExperienceDistribution(),
          analyticsApi.getFunnelMetrics(),
        ]);
        setMetrics(dash);
        setSkills(sk);
        setExperience(exp);
        setFunnel(fn);
      } catch (err) {
        console.error('Failed to load analytics', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Aggregating recruitment data & hiring trends..." size="lg" />;
  }

  const maxSkillCount = Math.max(...skills.map((s) => s.count), 1);
  const maxExpYears = Math.max(...experience.map((e) => e.avg_years), 1);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold mb-2">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>Talent & Hiring Insights</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Recruitment Analytics</h1>
        <p className="text-sm text-slate-500">
          Conversion funnels, skill demand trends, and candidate experience benchmarks.
        </p>
      </div>

      {/* Top Level Conversion Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <Card className="p-6">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Total Pipeline Applications
          </p>
          <p className="text-3xl font-extrabold text-slate-900 mt-2 font-mono">
            {metrics?.total_applications ?? 0}
          </p>
          <p className="text-xs text-slate-500 mt-1">Across {metrics?.active_jobs ?? 0} active requisitions</p>
        </Card>

        <Card className="p-6">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Application to Hire Rate
          </p>
          <p className="text-3xl font-extrabold text-emerald-600 mt-2 font-mono">
            {metrics?.conversion_rate_percentage ?? 0}%
          </p>
          <p className="text-xs text-slate-500 mt-1">{metrics?.hired_candidates ?? 0} confirmed hires</p>
        </Card>

        <Card className="p-6">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Indexed Technical Skills
          </p>
          <p className="text-3xl font-extrabold text-indigo-600 mt-2 font-mono">
            {skills.length}
          </p>
          <p className="text-xs text-slate-500 mt-1">Extracted automatically via PyPDF parsing</p>
        </Card>
      </div>

      {/* Funnel & Skills Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recruitment Conversion Funnel */}
        <Card className="p-6">
          <div className="mb-6 pb-4 border-b border-slate-100">
            <h2 className="text-lg font-bold text-slate-900">Application Stage Funnel</h2>
            <p className="text-xs text-slate-500">Candidate flow from submission to confirmed hire</p>
          </div>

          <div className="space-y-4">
            {funnel.map((item, idx) => {
              const maxCount = funnel[0]?.count || 1;
              const barWidth = Math.max(Math.round((item.count / maxCount) * 100), 8);
              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-800">{item.stage}</span>
                    <span className="font-mono text-slate-500 font-bold">
                      {item.count} candidates
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>

        {/* Most Prevalent Candidate Skills */}
        <Card className="p-6">
          <div className="mb-6 pb-4 border-b border-slate-100">
            <h2 className="text-lg font-bold text-slate-900">Top Candidate Skills</h2>
            <p className="text-xs text-slate-500">Frequency of technical skills across resumes</p>
          </div>

          <div className="space-y-4">
            {skills.slice(0, 7).map((item, idx) => {
              const widthPct = Math.max(Math.round((item.count / maxSkillCount) * 100), 8);
              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-800">{item.skill}</span>
                    <span className="font-mono text-slate-500 font-bold">
                      {item.count} profiles ({item.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-emerald-500 to-teal-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${widthPct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      {/* Average Experience by Skill */}
      <Card className="p-6">
        <div className="mb-6 pb-4 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-900">Experience Benchmarks</h2>
          <p className="text-xs text-slate-500">Average years of professional experience per technology</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {experience.slice(0, 8).map((exp, idx) => (
            <div key={idx} className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl">
              <p className="text-xs font-semibold text-slate-700">{exp.skill}</p>
              <p className="text-2xl font-bold font-mono text-indigo-700 mt-1">
                {exp.avg_years.toFixed(1)} <span className="text-xs font-normal text-slate-500">years</span>
              </p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
