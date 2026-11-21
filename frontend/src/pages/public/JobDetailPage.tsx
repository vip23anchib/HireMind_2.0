import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Briefcase,
  MapPin,
  Clock,
  ArrowLeft,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  FileText,
  Sparkles,
} from 'lucide-react';
import { jobsApi } from '../../api/jobs';
import { applicationsApi } from '../../api/applications';
import { Job, Application } from '../../types';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { AtsScoreBadge } from '../../components/resume/AtsScoreBadge';

export const JobDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Form states
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [gender, setGender] = useState('Prefer not to say');
  const [phone, setPhone] = useState('');
  const [country, setCountry] = useState('United States');
  const [coverLetter, setCoverLetter] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [submittedApplication, setSubmittedApplication] = useState<Application | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      if (!slug) return;
      setIsLoading(true);
      try {
        const data = await jobsApi.getJob(slug);
        setJob(data);
      } catch (err) {
        console.error('Failed to load job', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchJob();
  }, [slug]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setErrorMessage('Only PDF documents are supported.');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setErrorMessage('File size must not exceed 5MB.');
        return;
      }
      setErrorMessage(null);
      setResumeFile(file);
    }
  };

  const handleSubmitApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!job || !resumeFile) {
      setErrorMessage('Please select your resume PDF document.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('job', job.id.toString());
    formData.append('name', fullName);
    formData.append('email', email);
    formData.append('gender', gender);
    formData.append('phone_number', phone);
    formData.append('country', country);
    formData.append('cover_letter', coverLetter);
    formData.append('resume_file', resumeFile);

    try {
      const app = await applicationsApi.submitApplication(formData);
      setSubmittedApplication(app);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit application.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading position requirements..." size="lg" />;
  }

  if (!job) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl font-bold text-slate-800">Job position not found</h2>
        <Link to="/careers" className="text-indigo-600 hover:underline text-sm mt-2 inline-block">
          &larr; Back to open positions
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Back Link */}
      <Link
        to="/careers"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to All Openings</span>
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Job Details */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-8">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="text-xs font-semibold text-indigo-600">{job.department}</span>
              <span className="text-xs text-slate-300">&bull;</span>
              <span className="text-xs text-slate-500 font-medium">{job.job_type}</span>
            </div>

            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{job.title}</h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-4 pb-6 border-b border-slate-100">
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4 text-slate-400" />
                {job.location}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4 text-slate-400" />
                {job.experience_required}+ Years Experience
              </span>
            </div>

            {/* Description */}
            <div className="mt-6 space-y-6 text-sm text-slate-700 leading-relaxed">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-2">
                  About the Role
                </h3>
                <p className="whitespace-pre-line">{job.description}</p>
              </div>

              {job.responsibilities && (
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-2">
                    Key Responsibilities
                  </h3>
                  <p className="whitespace-pre-line">{job.responsibilities}</p>
                </div>
              )}

              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-2">
                  Requirements & Qualifications
                </h3>
                <p className="whitespace-pre-line">{job.requirements}</p>
              </div>

              {job.required_skills && job.required_skills.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-2">
                    Required Technical Skills
                  </h3>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {job.required_skills.map((s) => (
                      <span
                        key={s.id}
                        className="px-2.5 py-1 bg-indigo-50 border border-indigo-200 text-indigo-700 rounded-lg text-xs font-medium"
                      >
                        {s.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right: Application Form */}
        <div>
          <Card className="p-6 sticky top-24">
            {submittedApplication ? (
              <div className="text-center py-6 space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-slate-900">Application Received!</h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Thank you for applying for <strong>{job.title}</strong>. Your resume has been parsed and queued in our ATS pipeline.
                </p>

                {submittedApplication.ats_score !== undefined && (
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Initial ATS Match Rating
                    </p>
                    <AtsScoreBadge score={submittedApplication.ats_score} size="lg" />
                  </div>
                )}

                <Button
                  onClick={() => {
                    setSubmittedApplication(null);
                    setFullName('');
                    setEmail('');
                    setResumeFile(null);
                  }}
                  variant="outline"
                  size="sm"
                  className="w-full mt-4"
                >
                  Submit Another Application
                </Button>
              </div>
            ) : (
              <div>
                <h3 className="text-lg font-bold text-slate-900 mb-1">Apply for Position</h3>
                <p className="text-xs text-slate-500 mb-5">
                  Complete this application with your resume PDF.
                </p>

                {errorMessage && (
                  <div className="mb-4 flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{errorMessage}</span>
                  </div>
                )}

                <form onSubmit={handleSubmitApplication} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Jane Doe"
                      required
                      className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="jane@example.com"
                      required
                      className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Phone
                      </label>
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+1 555-0100"
                        className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Country
                      </label>
                      <input
                        type="text"
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        placeholder="United States"
                        className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                  </div>

                  {/* Resume Upload Area */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Resume Document (PDF) *
                    </label>
                    <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-200 hover:border-indigo-500 rounded-xl bg-slate-50/50 cursor-pointer transition-colors">
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="hidden"
                        required
                      />
                      {resumeFile ? (
                        <div className="flex items-center gap-2 text-indigo-600 text-xs font-semibold">
                          <FileText className="w-4 h-4" />
                          <span className="truncate max-w-[180px]">{resumeFile.name}</span>
                        </div>
                      ) : (
                        <div className="text-center">
                          <UploadCloud className="w-6 h-6 text-indigo-500 mx-auto mb-1" />
                          <span className="text-xs font-medium text-slate-600">Choose PDF file</span>
                          <p className="text-[10px] text-slate-400 mt-0.5">Up to 5MB</p>
                        </div>
                      )}
                    </label>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Cover Letter (Optional)
                    </label>
                    <textarea
                      rows={3}
                      value={coverLetter}
                      onChange={(e) => setCoverLetter(e.target.value)}
                      placeholder="Why are you a great match for this position?"
                      className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    isLoading={isSubmitting}
                    className="w-full mt-2"
                  >
                    Submit Application
                  </Button>
                </form>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
