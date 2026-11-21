import React, { useEffect, useState } from 'react';
import { Clock, User, CheckCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { activityApi } from '../../api/activity';
import { ActivityLog } from '../../types';
import { Card } from '../../components/common/Card';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export const ActivityPage: React.FC = () => {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fetchLogs = async (pageNum: number) => {
    setIsLoading(true);
    try {
      const data = await activityApi.getActivityLogs({ page: pageNum });
      setLogs(data.results);
      setTotalCount(data.count);
      setHasNext(!!data.next);
      setHasPrev(!!data.previous);
    } catch (err) {
      console.error('Failed to load activity logs', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs(page);
  }, [page]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Audit & Activity Trail</h1>
        <p className="text-sm text-slate-500">
          Immutable log of all recruitment events, status updates, and automated system actions.
        </p>
      </div>

      <Card className="overflow-hidden">
        {isLoading ? (
          <LoadingSpinner message="Fetching activity log stream..." />
        ) : logs.length === 0 ? (
          <p className="text-center py-12 text-sm text-slate-400">No activity events recorded yet.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {logs.map((log) => (
              <div key={log.id} className="p-4 flex items-start gap-3.5 hover:bg-slate-50/50 transition-colors">
                <div className="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 shrink-0 mt-0.5">
                  <Clock className="w-4 h-4" />
                </div>
                <div className="flex-1 text-xs">
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-slate-800 text-sm">
                      {log.action}
                    </p>
                    <span className="text-slate-400 font-mono">
                      {new Date(log.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-500 mt-1">
                    <span>Actor: <strong>{log.performed_by_name || 'System / Automated'}</strong></span>
                    {log.candidate_name && (
                      <>
                        <span>&bull;</span>
                        <span>Candidate: <strong>{log.candidate_name}</strong></span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Total {totalCount} events</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={!hasPrev || isLoading}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono font-semibold px-2">Page {page}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasNext || isLoading}
              className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};
