import React, { useEffect, useState } from 'react';
import {
  Users,
  Search,
  FileText,
  Download,
  Mail,
  Phone,
  Globe,
  UploadCloud,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import { candidatesApi } from '../../api/candidates';
import { Candidate } from '../../types';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { ResumeUploader } from '../../components/resume/ResumeUploader';
import { AtsScoreBadge } from '../../components/resume/AtsScoreBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';

export const CandidatesPage: React.FC = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const fetchCandidates = async () => {
    setIsLoading(true);
    try {
      const data = await candidatesApi.getCandidates();
      setCandidates(data.results);
    } catch (err) {
      console.error('Failed to load candidates', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  const handleOpenDetail = async (cand: Candidate) => {
    try {
      const detailed = await candidatesApi.getCandidate(cand.id);
      setSelectedCandidate(detailed);
      setIsDetailModalOpen(true);
    } catch {
      setSelectedCandidate(cand);
      setIsDetailModalOpen(true);
    }
  };

  const filteredCandidates = candidates.filter((c) => {
    const q = searchQuery.toLowerCase();
    const matchesNameOrEmail = c.name.toLowerCase().includes(q) || c.email.toLowerCase().includes(q);
    const matchesSkills = c.skills?.some((s) => s.name.toLowerCase().includes(q));
    return matchesNameOrEmail || matchesSkills;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Candidate Database</h1>
          <p className="text-sm text-slate-500">
            Talent roster, indexed skills, resumes, and recruitment history.
          </p>
        </div>
        <Button
          onClick={() => setIsUploadModalOpen(true)}
          variant="primary"
          icon={<UploadCloud className="w-4 h-4" />}
        >
          Add Candidate / Ingest Resume
        </Button>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by candidate name, email, or skill (e.g. Python, React)..."
          className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-2xs"
        />
      </div>

      {/* Candidates Table */}
      {isLoading ? (
        <LoadingSpinner message="Loading candidate profiles..." />
      ) : filteredCandidates.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No candidates found"
          description="Try a different search query or upload candidate resumes."
          actionLabel="Ingest Resume"
          onAction={() => setIsUploadModalOpen(true)}
        />
      ) : (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50/80 border-b border-slate-200/80 text-xs font-semibold uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="py-3.5 px-6">Candidate</th>
                  <th className="py-3.5 px-6">Current Status</th>
                  <th className="py-3.5 px-6">Latest ATS Match</th>
                  <th className="py-3.5 px-6">Core Skills</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredCandidates.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => handleOpenDetail(c)}
                    className="hover:bg-indigo-50/30 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-700 text-xs shrink-0">
                          {c.name ? c.name[0] : 'C'}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                            {c.name}
                          </p>
                          <p className="text-xs text-slate-400">{c.email}</p>
                        </div>
                      </div>
                    </td>

                    <td className="py-4 px-6">
                      <Badge status={c.current_status || 'Applied'} size="sm">
                        {c.current_status || 'Applied'}
                      </Badge>
                    </td>

                    <td className="py-4 px-6">
                      {c.latest_ats_score !== undefined && c.latest_ats_score !== null ? (
                        <AtsScoreBadge score={c.latest_ats_score} size="sm" />
                      ) : (
                        <span className="text-xs text-slate-400 italic">Not evaluated</span>
                      )}
                    </td>

                    <td className="py-4 px-6">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {c.skills && c.skills.length > 0 ? (
                          c.skills.slice(0, 3).map((sk, idx) => (
                            <span
                              key={idx}
                              className="text-[11px] px-2 py-0.5 bg-slate-100 text-slate-600 rounded font-medium"
                            >
                              {sk.name}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-slate-400 italic">No skills indexed</span>
                        )}
                        {c.skills && c.skills.length > 3 && (
                          <span className="text-[11px] px-1 py-0.5 text-slate-400">
                            +{c.skills.length - 3}
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="py-4 px-6 text-right">
                      <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 group-hover:translate-x-0.5 transition-transform">
                        <span>Profile</span>
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Candidate Detail Modal */}
      {selectedCandidate && (
        <Modal
          isOpen={isDetailModalOpen}
          onClose={() => setIsDetailModalOpen(false)}
          title={`Candidate Profile — ${selectedCandidate.name}`}
          maxWidth="2xl"
        >
          <div className="space-y-6">
            {/* Top Contact Bar */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 bg-slate-50 border border-slate-200/80 rounded-xl text-xs">
              <div className="flex items-center gap-2 text-slate-600">
                <Mail className="w-4 h-4 text-indigo-500 shrink-0" />
                <span className="truncate">{selectedCandidate.email}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600">
                <Phone className="w-4 h-4 text-indigo-500 shrink-0" />
                <span>{selectedCandidate.phone_number || 'N/A'}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600">
                <Globe className="w-4 h-4 text-indigo-500 shrink-0" />
                <span>{selectedCandidate.country || 'N/A'}</span>
              </div>
            </div>

            {/* Resume Download Action */}
            <div className="flex items-center justify-between p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-xs font-semibold text-slate-800">Verified Resume Document</p>
                  <p className="text-[11px] text-slate-500">Protected stream via authenticated API</p>
                </div>
              </div>
              <a
                href={candidatesApi.getResumeDownloadUrl(selectedCandidate.id)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download PDF</span>
              </a>
            </div>

            {/* Skills & Experience */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                Parsed Skills & Experience
              </h4>
              <div className="flex flex-wrap gap-2">
                {selectedCandidate.skills && selectedCandidate.skills.length > 0 ? (
                  selectedCandidate.skills.map((sk, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-800 shadow-2xs"
                    >
                      <span>{sk.name}</span>
                      {sk.years_of_experience > 0 && (
                        <span className="px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded text-[10px] font-mono">
                          {sk.years_of_experience}y
                        </span>
                      )}
                    </span>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 italic">No skills extracted.</p>
                )}
              </div>
            </div>

            {/* Application History */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                Job Applications
              </h4>
              {selectedCandidate.applications && selectedCandidate.applications.length > 0 ? (
                <div className="space-y-2">
                  {selectedCandidate.applications.map((app) => (
                    <div
                      key={app.id}
                      className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-xl text-xs"
                    >
                      <div>
                        <p className="font-semibold text-slate-800">{app.job_title}</p>
                        <p className="text-[11px] text-slate-400">
                          Applied {new Date(app.applied_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <AtsScoreBadge score={app.ats_score} size="sm" />
                        <Badge status={app.status} size="sm">
                          {app.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No active applications.</p>
              )}
            </div>
          </div>
        </Modal>
      )}

      {/* Upload Resume Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Ingest Candidate Resume"
        maxWidth="lg"
      >
        <ResumeUploader
          onSuccess={() => {
            fetchCandidates();
          }}
        />
      </Modal>
    </div>
  );
};
