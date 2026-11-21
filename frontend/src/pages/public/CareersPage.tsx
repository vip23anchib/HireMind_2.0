import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, MapPin, Clock, Search, ArrowRight, Sparkles } from 'lucide-react';
import { jobsApi } from '../../api/jobs';
import { Job } from '../../types';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const CareersPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('All');

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await jobsApi.getJobs({ is_active: true });
        setJobs(res.results);
      } catch (err) {
        console.error('Failed to load careers jobs', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const departments = ['All', ...Array.from(new Set(jobs.map((j) => j.department).filter(Boolean)))];

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(search.toLowerCase()) ||
      job.description.toLowerCase().includes(search.toLowerCase()) ||
      job.location.toLowerCase().includes(search.toLowerCase());
    const matchesDept = department === 'All' || job.department === department;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      {/* Hero Header */}
      <div className="text-center max-w-2xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>We're Actively Hiring</span>
        </div>
        <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight sm:text-5xl">
          Build the Future With HireMind
        </h1>
        <p className="text-slate-600 text-base leading-relaxed">
          Join our mission to transform recruitment with state-of-the-art applicant tracking, resume intelligence, and machine matching.
        </p>
      </div>

      {/* Search & Department Filters */}
      <div className="flex flex-col sm:flex-row gap-3 max-w-2xl mx-auto">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search open positions by role, skill, or location..."
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-2xs"
          />
        </div>
        <select
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          className="px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-2xs"
        >
          {departments.map((d) => (
            <option key={d} value={d}>
              {d === 'All' ? 'All Teams' : d}
            </option>
          ))}
        </select>
      </div>

      {/* Requisitions List */}
      {isLoading ? (
        <LoadingSpinner message="Loading available positions..." />
      ) : filteredJobs.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl p-8">
          <Briefcase className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-800">No positions found</h3>
          <p className="text-xs text-slate-500 mt-1">Try adjusting your search criteria or team filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filteredJobs.map((job) => (
            <Card key={job.id} hoverable className="p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-xs font-semibold text-indigo-600">{job.department}</span>
                  <span className="text-xs font-mono font-medium text-slate-400">{job.job_type}</span>
                </div>

                <h3 className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                  {job.title}
                </h3>

                <p className="text-xs text-slate-500 mt-2 line-clamp-2 leading-relaxed">
                  {job.description}
                </p>

                <div className="flex items-center gap-4 text-xs text-slate-500 mt-4">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    {job.location}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    {job.experience_required}+ Yrs Exp
                  </span>
                </div>

                {job.required_skills && job.required_skills.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-4">
                    {job.required_skills.map((sk) => (
                      <span
                        key={sk.id}
                        className="text-[11px] px-2 py-0.5 bg-slate-100 text-slate-600 rounded font-medium"
                      >
                        {sk.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-400">Apply online in 2 minutes</span>
                <Link
                  to={`/jobs/${job.slug || job.id}`}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition-colors"
                >
                  <span>View & Apply</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
