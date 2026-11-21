/**
 * Type Definitions for HireMind ATS
 * Matches Django DRF v1 REST API schemas
 */

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'Administrator' | 'Recruiter' | 'Staff';
  is_staff: boolean;
}

export interface Skill {
  id: number;
  name: string;
}

export interface UserSkill {
  id?: number;
  skill_id?: number;
  name: string;
  years_of_experience: number;
}

export interface Job {
  id: number;
  title: string;
  slug: string;
  department: string;
  location: string;
  job_type: 'Full Time' | 'Part Time' | 'Contract' | 'Internship' | 'Remote';
  description: string;
  requirements: string;
  responsibilities: string;
  experience_required: number;
  is_active: boolean;
  applications_count: number;
  required_skills: Skill[];
  created_at: string;
  updated_at: string;
}

export interface JobFormData {
  title: string;
  slug?: string;
  department: string;
  location: string;
  job_type: string;
  description: string;
  requirements: string;
  responsibilities: string;
  experience_required: number;
  is_active: boolean;
  required_skill_ids: number[];
}

export interface Candidate {
  id: number;
  name: string;
  email: string;
  gender: string;
  phone_number?: string;
  country: string;
  cover_letter?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  skills: UserSkill[];
  current_status?: string;
  latest_ats_score?: number;
  latest_job_title?: string;
  documents?: DocumentRecord[];
  applications?: ApplicationSummary[];
}

export interface DocumentRecord {
  id: number;
  status: 'Uploaded' | 'Queued' | 'Processing' | 'Completed' | 'Failed';
  error_message?: string;
  file_name?: string;
  file_url?: string;
  uploaded_at: string;
}

export interface Application {
  id: number;
  candidate_id: number;
  candidate_name: string;
  candidate_email: string;
  candidate_phone?: string;
  job_id: number;
  job_title: string;
  job_slug?: string;
  status: ApplicationStatus;
  ats_score: number;
  applied_at: string;
  updated_at: string;
  notes?: string;
  status_history?: ApplicationStatusHistory[];
}

export interface ApplicationSummary {
  id: number;
  job_id: number;
  job_title: string;
  status: ApplicationStatus;
  ats_score: number;
  applied_at: string;
}

export type ApplicationStatus =
  | 'Applied'
  | 'Under Review'
  | 'Shortlisted'
  | 'Interview Scheduled'
  | 'Technical Assessment'
  | 'Offer Extended'
  | 'Hired'
  | 'Rejected';

export interface ApplicationStatusHistory {
  id: number;
  old_status: string;
  new_status: string;
  changed_by?: string;
  notes?: string;
  changed_at: string;
}

export interface CandidateSearchResult {
  candidate: {
    id: number;
    name: string;
    email: string;
    phone: string;
    country: string;
  };
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  total_experience: number;
  has_resume: boolean;
}

export interface SearchResponse {
  search_type: 'and' | 'or';
  searched_skills: string[];
  min_experience: number;
  total_matches: number;
  results: CandidateSearchResult[];
}

export interface MatchAnalysisResponse {
  candidate_id: number;
  job_id: number;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  candidate_skills: string[];
  required_skills: string[];
  total_required: number;
  total_matched: number;
}

export interface DashboardMetrics {
  total_candidates: number;
  total_applications: number;
  total_jobs: number;
  active_jobs: number;
  hired_candidates: number;
  shortlisted_candidates: number;
  under_review: number;
  conversion_rate_percentage: number;
  recent_applications: Application[];
  pipeline_breakdown: Record<string, number>;
}

export interface SkillDistributionItem {
  skill: string;
  count: number;
  percentage: number;
}

export interface ExperienceDistributionItem {
  skill: string;
  avg_years: number;
}

export interface FunnelStage {
  stage: string;
  count: number;
  dropoff_rate: number;
}

export interface ActivityLog {
  id: number;
  action: string;
  performed_by_name: string;
  candidate_name?: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
