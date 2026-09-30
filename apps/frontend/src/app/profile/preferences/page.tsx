'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { apiRequest, API_BASE_URL } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Sparkles, X } from 'lucide-react';

export default function PreferencesPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Resume extraction state
  const [file, setFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionResult, setExtractionResult] = useState<any>(null);

  const [preferences, setPreferences] = useState({
    preferred_roles: [] as string[],
    preferred_states: [] as string[],
    preferred_cities: [] as string[],
    preferred_employment_types: [] as string[],
    preferred_work_modes: [] as string[],
    skills: [] as string[],
    min_salary: '',
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }

    const fetchPreferences = async () => {
      try {
        const data = await apiRequest('/users/me/preferences');
        if (data) {
          setPreferences({
            preferred_roles: data.preferred_roles || [],
            preferred_states: data.preferred_states || [],
            preferred_cities: data.preferred_cities || [],
            preferred_employment_types: data.preferred_employment_types || [],
            preferred_work_modes: data.preferred_work_modes || [],
            skills: data.skills || [],
            min_salary: data.min_salary ? String(data.min_salary) : '',
          });
        }
      } catch (err) {
        console.error('Failed to load preferences:', err);
      }
    };

    if (isAuthenticated) {
      fetchPreferences();
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) return null;

  const toggleArrayItem = (field: keyof typeof preferences, value: string) => {
    setPreferences(prev => {
      const array = prev[field] as string[];
      if (array.includes(value)) {
        return { ...prev, [field]: array.filter(i => i !== value) };
      }
      return { ...prev, [field]: [...array, value] };
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleExtractResume = async () => {
    if (!file) return;
    
    setIsExtracting(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(`${API_BASE_URL}/users/me/resume/extract`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to extract resume');
      }
      
      const data = await res.json();
      setExtractionResult(data);
      
      // Auto-fill the preferences state
      if (data.skills && data.skills.length > 0) {
        setPreferences(prev => ({
          ...prev,
          skills: Array.from(new Set([...prev.skills, ...data.skills]))
        }));
        setSuccess(`Successfully extracted ${data.skills.length} skills from your resume! Review and save below.`);
        setTimeout(() => setSuccess(''), 5000);
      } else {
        setError('No skills could be confidently extracted. Please enter them manually.');
      }
      
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An error occurred during resume extraction');
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError('');
    setSuccess('');
    
    try {
      const payload = {
        ...preferences,
        min_salary: preferences.min_salary ? parseInt(preferences.min_salary) : null,
      };

      await apiRequest('/users/me/preferences', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      
      setSuccess('Preferences saved successfully! Your For You feed is now active.');
      setTimeout(() => {
        router.push('/jobs?tab=for_you');
      }, 1500);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to save preferences');
    } finally {
      setIsSaving(false);
    }
  };

  const roles = ['Software Engineer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer', 'Data Scientist', 'Product Manager', 'DevOps Engineer', 'QA Engineer', 'UI/UX Designer'];
  const skills = ['React', 'Next.js', 'Python', 'Java', 'JavaScript', 'TypeScript', 'AWS', 'Docker', 'Kubernetes', 'SQL', 'PostgreSQL', 'MongoDB'];
  const workModes = ['Remote', 'Hybrid', 'On-site'];
  const employmentTypes = ['Full-time', 'Contract', 'Part-time', 'Internship'];

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight mb-2">
          Job Preferences
        </h2>
        <p className="text-gray-500 text-lg">
          Personalize your recommendations. Extract from resume or enter manually.
        </p>
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6 flex items-center">
          <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
          <p className="text-sm text-green-700">{success}</p>
        </div>
      )}

      {/* Parse Resume Section */}
      <div className="bg-[#FFF7ED] p-6 sm:p-8 rounded-2xl border border-orange-100 shadow-sm mb-8">
        <div className="flex flex-col md:flex-row gap-6 items-center">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-orange-600" />
              Auto-fill from Resume
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Upload your PDF resume and let our AI extract your skills automatically. You can review them below before saving.
            </p>
            <div className="flex items-center gap-4">
              <label className="cursor-pointer bg-white border border-gray-300 px-4 py-2 rounded-xl shadow-sm text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors">
                <span>Choose PDF File</span>
                <input type="file" className="sr-only" accept=".pdf" onChange={handleFileChange} />
              </label>
              
              {file && (
                <div className="flex items-center text-sm font-medium text-orange-700 bg-orange-100 px-3 py-2 rounded-xl">
                  <FileText className="h-4 w-4 mr-2" />
                  <span className="truncate max-w-[150px]">{file.name}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="w-full md:w-auto border-t md:border-t-0 md:border-l border-orange-200 pt-6 md:pt-0 md:pl-6">
            <Button 
              className="w-full bg-orange-600 hover:bg-orange-700 text-white rounded-xl py-6 font-bold"
              onClick={handleExtractResume}
              disabled={!file || isExtracting}
            >
              {isExtracting ? 'Extracting...' : 'Extract Skills'}
            </Button>
          </div>
        </div>
      </div>

      {/* Manual Entry Section */}
      <div className="space-y-8 bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
        
        {/* Roles Section */}
        <div>
          <h3 className="text-lg font-bold text-gray-900 mb-4">What roles are you looking for?</h3>
          <div className="flex flex-wrap gap-2">
            {roles.map(role => (
              <button
                key={role}
                onClick={() => toggleArrayItem('preferred_roles', role)}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all border ${
                  preferences.preferred_roles.includes(role)
                    ? 'bg-orange-50 text-orange-600 border-orange-200 shadow-sm'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        <hr className="border-gray-100" />

        {/* Skills Section */}
        <div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">Core Skills</h3>
          <p className="text-sm text-gray-500 mb-4">Select from common skills or extract from your resume above.</p>
          <div className="flex flex-wrap gap-2 mb-4">
            {preferences.skills.map(skill => (
              <button
                key={skill}
                onClick={() => toggleArrayItem('skills', skill)}
                className="px-4 py-2 rounded-full text-sm font-semibold transition-all border bg-orange-50 text-orange-600 border-orange-200 shadow-sm flex items-center gap-1"
              >
                {skill}
                <X className="w-3 h-3 ml-1 opacity-60" />
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            {skills.filter(s => !preferences.skills.includes(s)).map(skill => (
              <button
                key={skill}
                onClick={() => toggleArrayItem('skills', skill)}
                className="px-4 py-2 rounded-full text-sm font-semibold transition-all border bg-white text-gray-600 border-gray-200 hover:border-gray-300 hover:bg-gray-50"
              >
                + {skill}
              </button>
            ))}
          </div>
        </div>

        <hr className="border-gray-100" />

        {/* Work Mode & Type Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Preferred Work Mode</h3>
            <div className="flex flex-wrap gap-2">
              {workModes.map(mode => (
                <button
                  key={mode}
                  onClick={() => toggleArrayItem('preferred_work_modes', mode)}
                  className={`px-4 py-2 rounded-full text-sm font-semibold transition-all border ${
                    preferences.preferred_work_modes.includes(mode)
                      ? 'bg-orange-50 text-orange-600 border-orange-200 shadow-sm'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">Employment Type</h3>
            <div className="flex flex-wrap gap-2">
              {employmentTypes.map(type => (
                <button
                  key={type}
                  onClick={() => toggleArrayItem('preferred_employment_types', type)}
                  className={`px-4 py-2 rounded-full text-sm font-semibold transition-all border ${
                    preferences.preferred_employment_types.includes(type)
                      ? 'bg-orange-50 text-orange-600 border-orange-200 shadow-sm'
                      : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        <hr className="border-gray-100" />
        
        {/* Salary Section */}
        <div>
          <h3 className="text-lg font-bold text-gray-900 mb-4">Minimum Expected Salary (₹)</h3>
          <input
            type="number"
            placeholder="e.g. 1500000"
            className="mt-1 block w-full max-w-sm px-4 py-3 rounded-xl border border-gray-200 shadow-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 sm:text-sm transition-all"
            value={preferences.min_salary}
            onChange={(e) => setPreferences(prev => ({ ...prev, min_salary: e.target.value }))}
          />
        </div>

        <div className="pt-6 flex justify-end gap-4 border-t border-gray-100">
          <Button variant="outline" onClick={() => router.push('/jobs')} className="rounded-xl px-6 py-5 font-semibold text-gray-600">
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={isSaving} className="rounded-xl px-8 py-5 bg-orange-600 hover:bg-orange-700 font-bold shadow-md shadow-orange-500/20">
            {isSaving ? 'Saving...' : 'Save Preferences'}
          </Button>
        </div>
      </div>
    </div>
  );
}
