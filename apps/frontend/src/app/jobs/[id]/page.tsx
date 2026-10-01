import { Metadata } from 'next';
import Link from 'next/link';
import { fetchJobById } from '../../../lib/api';
import { ArrowLeft, Building2, MapPin, Briefcase, ExternalLink, Clock, Calendar, DollarSign, Lightbulb } from 'lucide-react';
import { notFound } from 'next/navigation';
import { ApplyButton } from '@/components/ApplyButton';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  try {
    const id = (await params).id;
    const job = await fetchJobById(id);
    return {
      title: `${job.title} at ${job.company.display_name}`,
    };
  } catch {
    return { title: 'Job Not Found' };
  }
}

export default async function JobDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  let job;
  try {
    const id = (await params).id;
    job = await fetchJobById(id);
  } catch (err) {
    notFound();
  }

  // Format posted date
  const postedDate = job.first_seen_at ? new Date(job.first_seen_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }) : null;

  return (
    <main className="min-h-screen bg-[#FDFBF7] pb-20">
      {/* Header section */}
      <div className="bg-white border-b border-gray-100 shadow-sm pt-8 pb-12">
        <div className="container mx-auto px-4 sm:px-8 max-w-5xl">
          <Link 
            href="/jobs" 
            className="inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-orange-600 transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Jobs
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
            <div className="flex gap-6">
              <div className="w-16 h-16 sm:w-20 sm:h-20 bg-orange-50 rounded-2xl flex items-center justify-center shrink-0 border border-orange-100 overflow-hidden">
                {job.company.logo_url ? (
                  <img src={job.company.logo_url} alt={job.company.display_name} className="w-full h-full object-cover" />
                ) : (
                  <Building2 className="w-8 h-8 text-orange-500" />
                )}
              </div>
              
              <div>
                <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-2 tracking-tight">
                  {job.title}
                </h1>
                <div className="text-lg text-gray-600 font-medium mb-4 flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-gray-400" />
                  {job.company.display_name}
                </div>
                
                <div className="flex flex-wrap items-center gap-x-6 gap-y-3 text-sm font-medium text-gray-500">
                  {job.location && (
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{job.location}</span>
                    </div>
                  )}
                  {job.work_mode && (
                    <div className="flex items-center gap-1.5">
                      <Briefcase className="w-4 h-4 text-gray-400" />
                      <span>{job.work_mode}</span>
                    </div>
                  )}
                  {job.employment_type && (
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span>{job.employment_type}</span>
                    </div>
                  )}
                  {job.experience_level && (
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span>Exp: {job.experience_level}</span>
                    </div>
                  )}
                  {postedDate && (
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span>Posted: {postedDate}</span>
                    </div>
                  )}
                  {(job as any).salary && (
                    <div className="flex items-center gap-1.5">
                      <DollarSign className="w-4 h-4 text-gray-400" />
                      <span>{(job as any).salary}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <ApplyButton applyUrl={job.apply_url} jobId={job.job_id} />
            </div>
          </div>
        </div>
      </div>
      
      {/* Content section */}
      <div className="container mx-auto px-4 sm:px-8 max-w-5xl mt-8 flex flex-col lg:flex-row gap-8">
        
        {/* Main Left Column (JD) */}
        <div className="flex-1">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 sm:p-10 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <FileTextIcon className="w-6 h-6 text-orange-500" />
              Job Description
            </h2>
            
            {!job.description ? (
              <div className="bg-orange-50 border border-orange-100 rounded-xl p-8 text-center">
                <p className="text-gray-600 font-medium">
                  Job description is not available for this job.
                </p>
              </div>
            ) : (
              <div className="whitespace-pre-line text-gray-700 leading-relaxed space-y-4 text-base font-normal">
                {job.description}
              </div>
            )}
          </div>
        </div>
        
        {/* Right Sidebar (Company/Skills info) */}
        <div className="w-full lg:w-80 space-y-6">
          {((job.required_skills && job.required_skills.length > 0) || ((job as any).skills && (job as any).skills.length > 0)) && (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-orange-500" />
                Required Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {(job.required_skills || (job as any).skills).map((skill: string, idx: number) => (
                  <span key={idx} className="px-3 py-1.5 bg-orange-50 text-orange-700 text-sm font-semibold rounded-lg border border-orange-100">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4">About {job.company.display_name}</h3>
            {job.company.description ? (
              <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                {job.company.description}
              </p>
            ) : (
              <p className="text-sm text-gray-500 mb-4 italic">
                No company description available.
              </p>
            )}
            
            {job.company.website && (
              <a 
                href={job.company.website.startsWith('http') ? job.company.website : `https://${job.company.website}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-semibold text-orange-600 hover:text-orange-700 flex items-center gap-1"
              >
                Visit Website
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>
        
      </div>
    </main>
  );
}

// Simple icon component for JD
function FileTextIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" x2="8" y1="13" y2="13" />
      <line x1="16" x2="8" y1="17" y2="17" />
      <line x1="10" x2="8" y1="9" y2="9" />
    </svg>
  );
}
