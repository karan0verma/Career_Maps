'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { JobCard } from '@/components/JobCard';
import { apiRequest } from '@/lib/api';

export default function SavedJobsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const [savedJobs, setSavedJobs] = useState<any[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      loadSavedJobs();
    }
  }, [isAuthenticated]);

  const loadSavedJobs = async () => {
    try {
      const data = await apiRequest('/users/me/applied_jobs');
      setSavedJobs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setFetching(false);
    }
  };

  if (isLoading || fetching) {
    return <div className="container mx-auto p-12 text-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <div className="container mx-auto p-12 text-center">Please log in to view Applied Jobs.</div>;
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      <h1 className="text-3xl font-bold mb-8">Applied Jobs</h1>
      
      {savedJobs.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground bg-gray-50 rounded-xl">
          You haven't tracked any applied jobs yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {savedJobs.map((item) => (
            <JobCard key={item.job_id} job={item.job} />
          ))}
        </div>
      )}
    </div>
  );
}
