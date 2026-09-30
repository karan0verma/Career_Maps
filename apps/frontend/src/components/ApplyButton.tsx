'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { ExternalLink } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';

interface ApplyButtonProps {
  applyUrl: string | null | undefined;
}

export function ApplyButton({ applyUrl }: ApplyButtonProps) {
  const { isAuthenticated } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // Safeguard: Ensure Infosys links always have valid hiring entity query params
  const getProcessedUrl = (url: string | null | undefined) => {
    if (!url) return '';
    let finalUrl = url.trim();
    if (finalUrl.includes('career.infosys.com/jobdesc') && !finalUrl.includes('companyhiringtype')) {
      const sep = finalUrl.includes('?') ? '&' : '?';
      finalUrl = `${finalUrl}${sep}companyhiringtype=IL&countrycode=IN`;
    }
    return finalUrl;
  };

  const finalApplyUrl = getProcessedUrl(applyUrl);

  const handleApplyClick = (e: React.MouseEvent) => {
    if (!isAuthenticated) {
      e.preventDefault();
      setShowModal(true);
    } else {
      // Authenticated user, open the link in a new tab with clean headers
      if (finalApplyUrl) {
        window.open(finalApplyUrl, '_blank', 'noopener');
      }
    }
  };

  const handleLoginRedirect = () => {
    // Optionally store redirect path to come back here after login
    // but the AuthContext or login page might handle that.
    // For now, we will use a simple query parameter.
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
        className="inline-flex justify-center items-center gap-2 w-full md:w-auto px-8 py-4 bg-orange-600 text-white font-bold rounded-xl hover:bg-orange-700 transition-all shadow-md shadow-orange-500/20 text-lg"
      >
        Apply Now
        <ExternalLink className="w-5 h-5" />
      </button>

      {showModal && (
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
                  onClick={() => setShowModal(false)}
                  className="w-full text-center py-2.5 text-orange-600 hover:text-orange-700 font-semibold text-sm hover:underline"
                >
                  Continue to Official Portal Directly &rarr;
                </a>
              )}
            </div>
            
            <button 
              onClick={() => setShowModal(false)}
              className="mt-6 text-sm text-gray-500 hover:text-gray-700 font-medium underline block text-center w-full"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </>
  );
}
