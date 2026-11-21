import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Sparkles,
  User,
  CheckCircle2,
  XCircle,
  Clock,
  Briefcase,
  FileText,
  SlidersHorizontal,
} from 'lucide-react';
import { searchApi } from '../../api/search';
import { CandidateSearchResult, SearchResponse } from '../../types';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { AtsScoreBadge } from '../../components/resume/AtsScoreBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';

const POPULAR_SKILLS = [
  'Python',
  'Django',
  'React.js',
  'PostgreSQL',
  'JavaScript',
  'TypeScript',
  'Docker',
  'AWS',
  'REST API',
  'SQL',
];

export const SearchPage: React.FC = () => {
  const [selectedSkills, setSelectedSkills] = useState<string[]>(['Python', 'Django']);
  const [skillInput, setSkillInput] = useState('');
  const [searchType, setSearchType] = useState<'and' | 'or'>('or');
  const [minExperience, setMinExperience] = useState<number>(0);
  const [searchResults, setSearchResults] = useState<CandidateSearchResult[]>([]);
  const [totalMatches, setTotalMatches] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);

  const performSearch = async () => {
    if (selectedSkills.length === 0) return;

    setIsLoading(true);
    try {
      const response = await searchApi.searchCandidates({
        skill: selectedSkills.join(','),
        search_type: searchType,
        min_experience: minExperience > 0 ? minExperience : undefined,
      });
      setSearchResults(response.results);
      setTotalMatches(response.total_matches);
    } catch (err) {
      console.error('Failed to perform ATS candidate search', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    performSearch();
  }, [selectedSkills, searchType, minExperience]);

  const handleAddSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (trimmed && !selectedSkills.includes(trimmed)) {
      setSelectedSkills([...selectedSkills, trimmed]);
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setSelectedSkills(selectedSkills.filter((s) => s !== skillToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      handleAddSkill(skillInput);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>ATS Candidate Search Engine</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Intelligent Talent Search & Skill Matching
        </h1>
        <p className="text-sm text-slate-500">
          Rank candidates against skill requirements with Boolean AND/OR filters and experience thresholds.
        </p>
      </div>

      {/* Search Controls Card */}
      <Card className="p-6 bg-white space-y-5">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
            Target Skills
          </label>
          <div className="flex flex-wrap items-center gap-2 p-2 bg-slate-50 border border-slate-200 rounded-xl min-h-[46px]">
            {selectedSkills.map((sk) => (
              <span
                key={sk}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-indigo-200 rounded-lg text-xs font-semibold text-indigo-700 shadow-2xs"
              >
                <span>{sk}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveSkill(sk)}
                  className="hover:text-rose-600 text-slate-400 font-bold"
                >
                  &times;
                </button>
              </span>
            ))}
            <input
              type="text"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={selectedSkills.length === 0 ? "Type a skill (e.g. Python, React) and press Enter..." : "Add skill..."}
              className="flex-1 bg-transparent border-none text-xs text-slate-800 placeholder-slate-400 focus:outline-none min-w-[120px] py-1"
            />
          </div>

          {/* Quick Suggestions */}
          <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
            <span className="text-[11px] text-slate-400">Suggestions:</span>
            {POPULAR_SKILLS.map((sk) => (
              <button
                key={sk}
                type="button"
                onClick={() => handleAddSkill(sk)}
                className={`text-[11px] px-2 py-0.5 rounded-md transition-colors ${
                  selectedSkills.includes(sk)
                    ? 'bg-indigo-100 text-indigo-800 font-semibold'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
              >
                + {sk}
              </button>
            ))}
          </div>
        </div>

        {/* Filters Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
          {/* Boolean Match Type */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
              Match Logic
            </label>
            <div className="inline-flex p-1 bg-slate-100 rounded-xl border border-slate-200">
              <button
                type="button"
                onClick={() => setSearchType('or')}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  searchType === 'or'
                    ? 'bg-white text-indigo-700 shadow-2xs font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                OR (Matches Any Skill)
              </button>
              <button
                type="button"
                onClick={() => setSearchType('and')}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  searchType === 'and'
                    ? 'bg-white text-indigo-700 shadow-2xs font-bold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                AND (Must Have All Skills)
              </button>
            </div>
          </div>

          {/* Minimum Experience */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
                Min Total Experience
              </label>
              <span className="text-xs font-mono font-bold text-indigo-600">
                {minExperience === 0 ? 'Any Experience' : `${minExperience}+ Years`}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="15"
              step="1"
              value={minExperience}
              onChange={(e) => setMinExperience(parseInt(e.target.value))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
          </div>
        </div>
      </Card>

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-500 px-1">
        <span>
          Showing <strong className="text-slate-800">{searchResults.length}</strong> matching candidate(s)
        </span>
        <span className="font-mono">Ranked by ATS Match Score</span>
      </div>

      {/* Results Grid */}
      {isLoading ? (
        <LoadingSpinner message="Calculating ATS match scores..." />
      ) : searchResults.length === 0 ? (
        <EmptyState
          icon={Search}
          title="No candidates match your criteria"
          description="Try switching to OR logic or lowering the minimum experience threshold."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {searchResults.map((res) => (
            <Card key={res.candidate.id} hoverable className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <h3 className="font-bold text-base text-slate-900">
                      {res.candidate.name}
                    </h3>
                    <p className="text-xs text-slate-400">{res.candidate.email}</p>
                  </div>
                  <AtsScoreBadge score={res.score} size="md" />
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-500 mb-4">
                  <span className="flex items-center gap-1 font-mono font-medium">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    {res.total_experience} Yrs Total Exp
                  </span>
                  <span>&bull;</span>
                  <span>{res.candidate.country}</span>
                </div>

                {/* Skills Analysis */}
                <div className="space-y-2 pt-3 border-t border-slate-100">
                  {res.matched_skills && res.matched_skills.length > 0 && (
                    <div>
                      <p className="text-[11px] font-semibold text-emerald-700 mb-1 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>Matched Skills ({res.matched_skills.length})</span>
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {res.matched_skills.map((s) => (
                          <span
                            key={s}
                            className="text-[11px] px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200/60 rounded font-medium"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {res.missing_skills && res.missing_skills.length > 0 && (
                    <div>
                      <p className="text-[11px] font-semibold text-slate-400 mb-1 flex items-center gap-1">
                        <XCircle className="w-3 h-3 text-slate-400" />
                        <span>Missing Skills ({res.missing_skills.length})</span>
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {res.missing_skills.map((s) => (
                          <span
                            key={s}
                            className="text-[11px] px-2 py-0.5 bg-slate-100 text-slate-500 border border-slate-200 rounded font-medium"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-400">
                  {res.has_resume ? 'PDF Resume Available' : 'No resume file'}
                </span>
                <a
                  href={`/api/v1/candidates/${res.candidate.id}/resume/`}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                >
                  <span>Review Profile</span>
                  <span>&rarr;</span>
                </a>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
