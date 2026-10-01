'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { ExternalLink, CheckCircle } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';
import { apiRequest } from '@/lib/api';

interface ApplyButtonProps {
  applyUrl: string | null | undefined;
  jobId: string;
}

export function ApplyButton({ applyUrl, jobId }: ApplyButtonProps) {
  const { isAuthenticated } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check if already applied
    if (isAuthenticated && jobId) {
      apiRequest(`/users/me/applied_jobs`).then(appliedJobs => {
        if (appliedJobs && appliedJobs.some((j: any) => j.job_id === jobId)) {
          setIsApplied(true);
        }
      }).catch(() => {});
    }
  }, [isAuthenticated, jobId]);

  const finalApplyUrl = applyUrl ? applyUrl.trim() : '';

  const handleApplyClick = (e: React.MouseEvent) => {
    if (!isAuthenticated) {
      e.preventDefault();
      setShowLoginModal(true);
    } else {
      if (finalApplyUrl) {
        window.open(finalApplyUrl, '_blank', 'noopener');
        if (!isApplied) {
          // Show feedback modal after a short delay
          setTimeout(() => setShowFeedbackModal(true), 1500);
        }
      }
    }
  };

  const confirmApplication = async (applied: boolean) => {
    setShowFeedbackModal(false);
    if (applied) {
      setIsUpdating(true);
      try {
        await apiRequest(`/users/me/applied_jobs?job_id=${jobId}`, { method: 'POST' });
        setIsApplied(true);
      } catch (err) {
        console.error("Failed to save applied status", err);
      } finally {
        setIsUpdating(false);
      }
    }
  };

  const handleLoginRedirect = () => {
    router.push(`/login?redirect=${encodeURIComponent(pathname)}`);
  };

  const handleSignupRedirect = () => {
    router.push(`/register?redirect=${encodeURIComponent(pathname)}`);
  };

  if (!applyUrl || applyUrl.trim() === '') {
    return (
      <button 
        disabled
        className="inline-flex justify-center items-center gap-2 w-full md:w-auto px-8 py-4 bg-gray-300 text-gray-600 font-bold rounded-xl cursor-not-allowed shadow-none text-lg"
      >
        Application link is currently unavailable.
      </button>
    );
  }

  return (
    <>
      <button 
        onClick={handleApplyClick}
        disabled={isUpdating}
        className={`inline-flex justify-center items-center gap-2 w-full md:w-auto px-8 py-4 font-bold rounded-xl transition-all shadow-md text-lg ${isApplied ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-500/20' : 'bg-orange-600 hover:bg-orange-700 text-white shadow-orange-500/20'}`}
      >
        {isApplied ? (
          <>
            <CheckCircle className="w-5 h-5" />
            Applied
          </>
        ) : (
          <>
            Apply Now
            <ExternalLink className="w-5 h-5" />
          </>
        )}
      </button>

      {/* Login Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8 relative animate-in fade-in zoom-in duration-200">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Almost there!</h3>
            <p className="text-gray-600 mb-8">
              Please login to your Career Maps account before applying to this position.
            </p>
            
            <div className="flex flex-col gap-3">
              <button 
                onClick={handleLoginRedirect}
                className="w-full bg-orange-600 text-white font-bold py-3 rounded-xl hover:bg-orange-700 transition-colors shadow-sm"
              >
                Login to Save & Track Application
              </button>
              <button 
                onClick={handleSignupRedirect}
                className="w-full bg-white text-gray-700 font-bold py-3 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors shadow-sm"
              >
                Create Free Account
              </button>
              {finalApplyUrl && (
                <a
                  href={finalApplyUrl}
                  target="_blank"
                  rel="noopener"
                  onClick={() => setShowLoginModal(false)}
                  className="w-full text-center py-2.5 text-orange-600 hover:text-orange-700 font-semibold text-sm hover:underline"
                >
                  Continue to Official Portal Directly &rarr;
                </a>
              )}
            </div>
            
            <button 
              onClick={() => setShowLoginModal(false)}
              className="mt-6 text-sm text-gray-500 hover:text-gray-700 font-medium underline block text-center w-full"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 relative animate-in fade-in zoom-in duration-200 text-center">
            <div className="w-16 h-16 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Did you apply?</h3>
            <p className="text-gray-500 text-sm mb-6">
              Let us know if you successfully submitted your application on the company's portal.
            </p>
            
            <div className="flex flex-col gap-3">
              <button 
                onClick={() => confirmApplication(true)}
                className="w-full bg-emerald-600 text-white font-bold py-3 rounded-xl hover:bg-emerald-700 transition-colors shadow-sm"
              >
                Yes, I applied
              </button>
              <button 
                onClick={() => confirmApplication(false)}
                className="w-full bg-white text-gray-700 font-bold py-3 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors shadow-sm"
              >
                No, maybe later
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
