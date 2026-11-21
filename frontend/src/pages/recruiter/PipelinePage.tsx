import React, { useEffect, useState } from 'react';
import {
  GitBranch,
  Filter,
  ArrowRight,
  History,
  FileText,
  User,
  Briefcase,
  Check,
} from 'lucide-react';
import { applicationsApi } from '../../api/applications';
import { jobsApi } from '../../api/jobs';
import { Application, ApplicationStatus, Job, ApplicationStatusHistory } from '../../types';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { AtsScoreBadge } from '../../components/resume/AtsScoreBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

const PIPELINE_STAGES: ApplicationStatus[] = [
  'Applied',
  'Under Review',
  'Shortlisted',
  'Interview Scheduled',
  'Technical Assessment',
  'Offer Extended',
  'Hired',
];

export const PipelinePage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);

  // Transition modal state
  const [isMoveModalOpen, setIsMoveModalOpen] = useState(false);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [targetStatus, setTargetStatus] = useState<ApplicationStatus>('Under Review');
  const [notes, setNotes] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  // History modal state
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [historyList, setHistoryList] = useState<ApplicationStatusHistory[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  const fetchApplications = async () => {
    setIsLoading(true);
    try {
      const [appsRes, jobsRes] = await Promise.all([
        applicationsApi.getApplications({
          job: selectedJobId !== 'all' ? parseInt(selectedJobId) : undefined,
        }),
        jobsApi.getJobs(),
      ]);
      setApplications(appsRes.results);
      setJobs(jobsRes.results);
    } catch (err) {
      console.error('Failed to load applications', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [selectedJobId]);

  const handleOpenMoveModal = (app: Application) => {
    setSelectedApp(app);
    setTargetStatus(app.status);
    setNotes('');
    setIsMoveModalOpen(true);
  };

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedApp) return;

    setIsUpdating(true);
    try {
      const updated = await applicationsApi.updateStatus(selectedApp.id, targetStatus, notes);
      setApplications((prev) => prev.map((a) => (a.id === selectedApp.id ? updated : a)));
      setIsMoveModalOpen(false);
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleViewHistory = async (app: Application) => {
    setSelectedApp(app);
    setIsHistoryModalOpen(true);
    setIsLoadingHistory(true);
    try {
      const history = await applicationsApi.getStatusHistory(app.id);
      setHistoryList(history);
    } catch (err) {
      console.error('Failed to fetch status history', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header & Job Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Application Pipeline</h1>
          <p className="text-sm text-slate-500">
            Track candidate stages, review match ratings, and update recruitment milestones.
          </p>
        </div>

        {/* Filter by Job */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            className="px-3.5 py-2 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-2xs"
          >
            <option value="all">All Requisitions ({applications.length})</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner message="Organizing recruitment stages..." />
      ) : (
        /* Kanban Columns */
        <div className="flex gap-4 overflow-x-auto pb-6">
          {PIPELINE_STAGES.map((stage) => {
            const stageApps = applications.filter((a) => a.status === stage);
            return (
              <div
                key={stage}
                className="w-80 shrink-0 bg-slate-100/70 border border-slate-200 rounded-2xl p-4 flex flex-col max-h-[78vh]"
              >
                {/* Column Header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200/80">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-800">{stage}</span>
                    <span className="w-5 h-5 rounded-full bg-white border border-slate-200 text-[11px] font-mono font-bold flex items-center justify-center text-slate-600">
                      {stageApps.length}
                    </span>
                  </div>
                </div>

                {/* Candidate Cards in Stage */}
                <div className="space-y-3 overflow-y-auto flex-1 pr-1">
                  {stageApps.map((app) => (
                    <Card key={app.id} hoverable className="p-4 bg-white space-y-3">
                      <div>
                        <div className="flex items-start justify-between gap-1">
                          <p className="font-semibold text-sm text-slate-900 line-clamp-1">
                            {app.candidate_name}
                          </p>
                          <AtsScoreBadge score={app.ats_score} size="sm" showIcon={false} />
                        </div>
                        <p className="text-xs text-indigo-600 font-medium mt-0.5 line-clamp-1">
                          {app.job_title}
                        </p>
                        <p className="text-[11px] text-slate-400 mt-1">
                          Applied {new Date(app.applied_at).toLocaleDateString()}
                        </p>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                        <button
                          onClick={() => handleViewHistory(app)}
                          className="flex items-center gap-1 text-slate-400 hover:text-slate-700 transition-colors"
                          title="View Stage Transition History"
                        >
                          <History className="w-3.5 h-3.5" />
                          <span>History</span>
                        </button>

                        <button
                          onClick={() => handleOpenMoveModal(app)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-medium rounded-lg transition-colors"
                        >
                          <span>Move</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </Card>
                  ))}

                  {stageApps.length === 0 && (
                    <div className="text-center py-8 text-xs text-slate-400 italic">
                      No candidates in this stage
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Stage Transition Modal */}
      {selectedApp && (
        <Modal
          isOpen={isMoveModalOpen}
          onClose={() => setIsMoveModalOpen(false)}
          title={`Update Recruitment Stage — ${selectedApp.candidate_name}`}
          maxWidth="md"
        >
          <form onSubmit={handleStatusUpdate} className="space-y-4">
            <div>
              <p className="text-xs text-slate-500 mb-1">Applying for role:</p>
              <p className="text-sm font-semibold text-slate-800">{selectedApp.job_title}</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                New Recruitment Stage *
              </label>
              <select
                value={targetStatus}
                onChange={(e) => setTargetStatus(e.target.value as ApplicationStatus)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
              >
                {PIPELINE_STAGES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
                <option value="Rejected">Rejected</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Transition Notes / Feedback (Optional)
              </label>
              <textarea
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g. Cleared round 1 technical interview, strong communication skills..."
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <Button type="button" variant="outline" onClick={() => setIsMoveModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" isLoading={isUpdating}>
                Update Stage
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Status History Audit Timeline Modal */}
      {selectedApp && (
        <Modal
          isOpen={isHistoryModalOpen}
          onClose={() => setIsHistoryModalOpen(false)}
          title={`Stage History — ${selectedApp.candidate_name}`}
          maxWidth="md"
        >
          {isLoadingHistory ? (
            <LoadingSpinner message="Retrieving audit history..." size="sm" />
          ) : historyList.length === 0 ? (
            <p className="text-center py-6 text-xs text-slate-400 italic">No transition history logged yet.</p>
          ) : (
            <div className="space-y-4">
              {historyList.map((hist, idx) => (
                <div key={hist.id || idx} className="flex gap-3 relative pb-4">
                  {idx !== historyList.length - 1 && (
                    <div className="absolute left-3 top-6 bottom-0 w-0.5 bg-slate-200" />
                  )}
                  <div className="w-6 h-6 rounded-full bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 shrink-0 mt-0.5">
                    <Check className="w-3.5 h-3.5" />
                  </div>
                  <div className="flex-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-800">
                        {hist.old_status} &rarr; <span className="text-indigo-600">{hist.new_status}</span>
                      </span>
                      <span className="text-slate-400 text-[11px]">
                        {new Date(hist.changed_at).toLocaleString()}
                      </span>
                    </div>
                    {hist.changed_by && (
                      <p className="text-[11px] text-slate-500 mt-0.5">By {hist.changed_by}</p>
                    )}
                    {hist.notes && (
                      <p className="mt-1.5 p-2 bg-slate-50 border border-slate-100 rounded-lg text-slate-600 italic">
                        "{hist.notes}"
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Modal>
      )}
    </div>
  );
};
