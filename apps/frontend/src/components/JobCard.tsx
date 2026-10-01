'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Building2, MapPin, Briefcase, Bookmark, Check, ArrowUpRight } from 'lucide-react';
import { Job, apiRequest } from '../lib/api';
import { useAuth } from '@/context/AuthContext';

interface JobCardProps {
  job: Job;
  isForYou?: boolean;
  initialIsSaved?: boolean;
  onUnsave?: (jobId: string) => void;
}

export function JobCard({ job, isForYou, initialIsSaved = false, onUnsave }: JobCardProps) {
  const { isAuthenticated } = useAuth();
  const [isSaved, setIsSaved] = useState(initialIsSaved);
  const [logoError, setLogoError] = useState(false);

  const handleSave = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) return alert("Please log in to save jobs");
    
    try {
      if (isSaved) {
        await apiRequest(`/users/me/saved_jobs/${job.job_id}`, { method: 'DELETE' });
        setIsSaved(false);
        if (onUnsave) onUnsave(job.job_id);
      } else {
        await apiRequest(`/users/me/saved_jobs?job_id=${job.job_id}`, { method: 'POST' });
        setIsSaved(true);
      }
    } catch (err) {
      console.error("Failed to save job");
    }
  };

  const city = job.location ? job.location.split(',')[0].trim() : 'India';

  return (
    <div className="flex flex-col justify-between bg-white rounded-2xl border border-gray-200/90 shadow-xs hover:shadow-md hover:border-orange-200 transition-all p-3.5 sm:p-4 group">
      <div>
        {/* Header Row: Company Logo + Title + Bookmark */}
        <div className="flex items-start justify-between gap-2.5 mb-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-gray-50 flex items-center justify-center shrink-0 border border-gray-100 overflow-hidden shadow-2xs">
              {job.company.logo_url && !logoError ? (
                <img 
                  src={job.company.logo_url} 
                  alt={job.company.display_name} 
                  className="w-full h-full object-contain p-0.5" 
                  onError={() => setLogoError(true)}
                />
              ) : (
                <Building2 className="w-4 h-4 text-gray-400" />
              )}
            </div>
            <div className="min-w-0">
              <span className="text-[11px] font-semibold text-gray-500 truncate block">
                {job.company.display_name}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {isForYou && job.match_percentage !== undefined && (
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60">
                {job.match_percentage}%
              </span>
            )}
            <button 
              onClick={handleSave}
              className={`p-1.5 rounded-lg transition-colors ${
                isSaved 
                  ? 'text-orange-600 bg-orange-50' 
                  : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100'
              }`}
              title={isSaved ? "Saved" : "Save Job"}
            >
              <Bookmark className="w-4 h-4" fill={isSaved ? "currentColor" : "none"} />
            </button>
          </div>
        </div>

        {/* Job Title */}
        <h3 className="font-bold text-sm text-gray-900 leading-snug line-clamp-1 mb-2 group-hover:text-orange-600 transition-colors">
          {job.title}
        </h3>

        {/* Compact Metadata Chips */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-gray-500 mb-3">
          {city && (
            <span className="inline-flex items-center gap-1 bg-gray-50 px-2 py-0.5 rounded-md border border-gray-100 font-medium text-gray-600">
              <MapPin className="w-3 h-3 text-gray-400" />
              <span className="truncate max-w-[90px]">{city}</span>
            </span>
          )}
          {job.work_mode && (
            <span className="inline-flex items-center gap-1 bg-gray-50 px-2 py-0.5 rounded-md border border-gray-100 font-medium text-gray-600">
              <Briefcase className="w-3 h-3 text-gray-400" />
              <span>{job.work_mode}</span>
            </span>
          )}
          {job.employment_type && (
            <span className="hidden sm:inline-block bg-gray-50 px-1.5 py-0.5 rounded-md border border-gray-100 font-medium text-gray-500 text-[10px]">
              {job.employment_type}
            </span>
          )}
        </div>

        {/* Match reasons if in For You tab */}
        {isForYou && job.match_reasons && job.match_reasons.length > 0 && (
          <div className="mb-2.5 pt-2 border-t border-gray-100 text-[11px]">
            <div className="space-y-1">
              {job.match_reasons.slice(0, 2).map((reason, idx) => (
                <p key={idx} className="text-gray-600 flex items-center gap-1.5 truncate">
                  <Check className="w-3 h-3 text-emerald-500 shrink-0" />
                  <span className="truncate">{reason}</span>
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Footer Row: View Job CTA */}
      <div className="pt-2 border-t border-gray-100 flex items-center justify-between mt-auto">
        <span className="text-[10px] font-medium text-gray-400">
          Verified Opening
        </span>
        
        <Link 
          href={`/jobs/${job.job_id}`}
          className="inline-flex items-center gap-1 px-3 py-1 bg-orange-50 hover:bg-orange-100 text-orange-600 transition-colors rounded-lg font-bold text-xs group-hover:bg-orange-600 group-hover:text-white shadow-2xs"
          onClick={(e) => e.stopPropagation()}
        >
          View Job
          <ArrowUpRight className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
}
