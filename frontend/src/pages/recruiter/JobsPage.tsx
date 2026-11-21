import React, { useEffect, useState } from 'react';
import {
  Briefcase,
  Plus,
  Search,
  MapPin,
  Clock,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Users,
} from 'lucide-react';
import { jobsApi } from '../../api/jobs';
import { Job, JobFormData } from '../../types';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const initialForm: JobFormData = {
    title: '',
    slug: '',
    department: 'Engineering',
    location: 'Remote',
    job_type: 'Full Time',
    description: '',
    requirements: '',
    responsibilities: '',
    experience_required: 2,
    is_active: true,
    required_skill_ids: [],
  };

  const [formData, setFormData] = useState<JobFormData>(initialForm);

  const fetchJobs = async () => {
    setIsLoading(true);
    try {
      const data = await jobsApi.getJobs();
      setJobs(data.results);
    } catch (err) {
      console.error('Failed to load jobs', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleToggleStatus = async (id: number) => {
    try {
      const updated = await jobsApi.toggleJobStatus(id);
      setJobs((prev) => prev.map((j) => (j.id === id ? updated : j)));
    } catch (err: any) {
      alert(err.message || 'Failed to toggle job status.');
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormError(null);

    try {
      // Auto-generate slug if missing
      const slug = formData.slug || formData.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '');
      await jobsApi.createJob({ ...formData, slug });
      setIsModalOpen(false);
      setFormData(initialForm);
      await fetchJobs();
    } catch (err: any) {
      setFormError(err.message || 'Failed to create job posting.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const departments = ['All', ...Array.from(new Set(jobs.map((j) => j.department).filter(Boolean)))];

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.location.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDept = selectedDept === 'All' || job.department === selectedDept;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Job Requisitions</h1>
          <p className="text-sm text-slate-500">
            Create, publish, and manage hiring roles and candidate pipelines.
          </p>
        </div>
        <Button
          onClick={() => setIsModalOpen(true)}
          variant="primary"
          icon={<Plus className="w-4 h-4" />}
        >
          Post New Role
        </Button>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search roles by title, department, location..."
            className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex gap-2">
          <select
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            className="px-3.5 py-2 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept === 'All' ? 'All Departments' : dept}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Jobs Grid */}
      {isLoading ? (
        <LoadingSpinner message="Loading active requisitions..." />
      ) : filteredJobs.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No jobs found"
          description="Try modifying your search filter or post a new requisition."
          actionLabel="Post New Role"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredJobs.map((job) => (
            <Card key={job.id} hoverable className="p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <Badge variant={job.is_active ? 'success' : 'default'} size="sm">
                    {job.is_active ? 'Active' : 'Closed'}
                  </Badge>
                  <span className="text-xs font-mono font-medium text-slate-400">
                    {job.job_type}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1">
                  {job.title}
                </h3>
                <p className="text-xs font-medium text-indigo-600 mt-0.5">{job.department}</p>

                <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-slate-500 mt-4">
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
                    {job.required_skills.slice(0, 4).map((sk) => (
                      <span
                        key={sk.id}
                        className="text-[11px] px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md font-medium"
                      >
                        {sk.name}
                      </span>
                    ))}
                    {job.required_skills.length > 4 && (
                      <span className="text-[11px] px-1.5 py-0.5 text-slate-400">
                        +{job.required_skills.length - 4}
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                  <Users className="w-4 h-4 text-indigo-600" />
                  <span>{job.applications_count} Candidates</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggleStatus(job.id)}
                    className="text-xs font-medium px-2.5 py-1 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
                  >
                    {job.is_active ? 'Close' : 'Reopen'}
                  </button>
                  <a
                    href={`/jobs/${job.slug || job.id}`}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 text-slate-400 hover:text-indigo-600 transition-colors"
                    title="View Public Listing"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Job Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Post New Requisition"
        maxWidth="2xl"
      >
        {formError && (
          <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
            {formError}
          </div>
        )}

        <form onSubmit={handleCreateJob} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Role Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g. Senior Backend Engineer"
                required
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Department *</label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                placeholder="e.g. Engineering, Product, Design"
                required
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Location</label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="e.g. Remote, San Francisco"
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Work Type</label>
              <select
                value={formData.job_type}
                onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="Full Time">Full Time</option>
                <option value="Part Time">Part Time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
                <option value="Remote">Remote</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Min Experience (Yrs)</label>
              <input
                type="number"
                min="0"
                max="20"
                value={formData.experience_required}
                onChange={(e) => setFormData({ ...formData, experience_required: parseInt(e.target.value) || 0 })}
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Role Description *</label>
            <textarea
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the opportunity and team..."
              required
              className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Requirements (Skills & Tech) *</label>
            <textarea
              rows={3}
              value={formData.requirements}
              onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
              placeholder="e.g. Python, Django, PostgreSQL, Docker, Redis..."
              required
              className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isSubmitting}>
              Publish Requisition
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
