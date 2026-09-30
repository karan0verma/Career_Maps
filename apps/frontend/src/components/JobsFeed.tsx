'use client';

import React, { useState, useEffect } from 'react';
import { Search, MapPin, Briefcase, Award, Sparkles, X, ChevronDown, Building2 } from 'lucide-react';
import { JobCard } from './JobCard';
import { Job, fetchJobs, fetchRecommendedJobs, apiRequest } from '../lib/api';
import { useAuth } from '@/context/AuthContext';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { Button } from './ui/button';
import { LiveTickerFullWidthBanner } from './LiveTickerFullWidthBanner';

export function JobsFeed({ companyType }: { companyType?: string }) {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = searchParams.get('tab');
  const qParam = searchParams.get('q');
  const locParam = searchParams.get('location');
  const workModeParam = searchParams.get('work_mode');
  const domainParam = searchParams.get('domain');
  const expParam = searchParams.get('experience');
  const roleParam = searchParams.get('role');
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [query, setQuery] = useState(qParam || '');
  const [location, setLocation] = useState(locParam || '');
  const [workMode, setWorkMode] = useState(workModeParam || '');
  const [domain, setDomain] = useState(domainParam || '');
  const [experience, setExperience] = useState(expParam || '');
  const [role, setRole] = useState(roleParam || '');
  
  const [page, setPage] = useState(0);
  const [activeTab, setActiveTab] = useState<'for_you' | 'all'>((tabParam as any) || 'all');
  const [hasPreferences, setHasPreferences] = useState(true); // Default to true until checked
  const [showBanner, setShowBanner] = useState(true);
  
  // Autocomplete state
  interface Suggestion {
    id: string;
    type: 'job' | 'company';
    text: string;
    subtext?: string;
  }
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  
  const limit = 24;

  useEffect(() => {
    const checkPreferences = async () => {
      if (isAuthenticated) {
        try {
          const prefs = await apiRequest('/users/me/preferences');
          if (prefs && (prefs.preferred_roles?.length > 0 || prefs.skills?.length > 0)) {
            setHasPreferences(true);
            setShowBanner(false);
          } else {
            setHasPreferences(false);
            setShowBanner(true);
          }
        } catch (e) {
          setHasPreferences(false);
        }
      }
    };
    checkPreferences();
  }, [isAuthenticated]);

  useEffect(() => {
    if (tabParam === 'for_you' || tabParam === 'all') {
      setActiveTab(tabParam);
    }
    if (qParam !== null) setQuery(qParam);
    if (locParam !== null) setLocation(locParam);
    if (workModeParam !== null) setWorkMode(workModeParam);
    if (domainParam !== null) setDomain(domainParam);
    if (expParam !== null) setExperience(expParam);
    if (roleParam !== null) setRole(roleParam);
  }, [tabParam, qParam, locParam, workModeParam, domainParam, expParam, roleParam]);

  // Autocomplete effect
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length >= 2) {
        setIsSearching(true);
        try {
          const [jobsRes, compsRes] = await Promise.all([
            fetchJobs({ q: query, limit: 3 }),
            apiRequest(`/companies?search=${encodeURIComponent(query)}&limit=3`)
          ]);
          
          const newSuggestions: Suggestion[] = [];
          
          if (compsRes && compsRes.length > 0) {
            compsRes.forEach((c: any) => {
              newSuggestions.push({
                id: c.company_id,
                type: 'company',
                text: c.display_name,
                subtext: c.industry
              });
            });
          }
          
          if (jobsRes && jobsRes.length > 0) {
            jobsRes.forEach((j: any) => {
              newSuggestions.push({
                id: j.job_id,
                type: 'job',
                text: j.title,
                subtext: j.company?.display_name || j.location
              });
            });
          }
          
          setSuggestions(newSuggestions);
          setShowSuggestions(true);
        } catch (e) {
          console.error("Autocomplete error:", e);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300);
    
    return () => clearTimeout(timer);
  }, [query]);

  const loadJobs = async (
    reset = false, 
    tab = activeTab, 
    filterOverrides?: { domain?: string; experience?: string; role?: string; workMode?: string; location?: string; query?: string }
  ) => {
    try {
      setLoading(true);
      const newPage = reset ? 0 : page;
      
      let data: Job[] = [];
      
      if (tab === 'for_you' && isAuthenticated && hasPreferences) {
        data = await fetchRecommendedJobs(newPage * limit, limit);
      } else {
        // Prepare search params
        const params: any = { skip: newPage * limit, limit };
        const activeQ = filterOverrides?.query !== undefined ? filterOverrides.query : query;
        const activeLoc = filterOverrides?.location !== undefined ? filterOverrides.location : location;
        const activeWorkMode = filterOverrides?.workMode !== undefined ? filterOverrides.workMode : workMode;
        const activeDomain = filterOverrides?.domain !== undefined ? filterOverrides.domain : domain;
        const activeExp = filterOverrides?.experience !== undefined ? filterOverrides.experience : experience;
        const activeRole = filterOverrides?.role !== undefined ? filterOverrides.role : role;

        if (activeQ) params.q = activeQ;
        if (activeLoc) params.location = activeLoc;
        if (activeWorkMode) params.work_mode = activeWorkMode;
        if (activeDomain) params.domain = activeDomain;
        if (activeExp) params.experience = activeExp;
        if (activeRole) params.role = activeRole;
        if (companyType) params.company_type = companyType;
        
        data = await fetchJobs(params);
      }
      
      if (reset) {
        setJobs(data);
        setPage(1);
      } else {
        setJobs(prev => {
          const existing = new Set(prev.map(j => j.job_id));
          const fresh = data.filter(j => !existing.has(j.job_id));
          return [...prev, ...fresh];
        });
        setPage(newPage + 1);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'for_you' && !hasPreferences) {
      setJobs([]);
      setLoading(false);
      return;
    }
    loadJobs(true, activeTab);
  }, [activeTab, isAuthenticated, hasPreferences, domain, experience, role, workMode]);

  const handleTabChange = (tab: 'for_you' | 'all') => {
    router.push(`/jobs?tab=${tab}`);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    const searchParams = new URLSearchParams();
    searchParams.set('tab', 'all');
    if (query) searchParams.set('q', query);
    if (location) searchParams.set('location', location);
    if (workMode) searchParams.set('work_mode', workMode);
    if (domain) searchParams.set('domain', domain);
    if (experience) searchParams.set('experience', experience);
    if (role) searchParams.set('role', role);
    
    if (isDashboard || activeTab === 'for_you') {
      router.push(`/jobs?${searchParams.toString()}`);
    } else {
      window.history.pushState(null, '', `/jobs?${searchParams.toString()}`);
      loadJobs(true, 'all');
    }
  };

  const handleClearFilters = () => {
    setQuery('');
    setLocation('');
    setWorkMode('');
    setDomain('');
    setExperience('');
    setRole('');
    window.history.pushState(null, '', `/jobs?tab=all`);
    loadJobs(true, 'all', { query: '', location: '', workMode: '', domain: '', experience: '', role: '' });
  };

  const pathname = usePathname();
  const isDashboard = pathname === '/';

  return (
    <div className="py-6 px-4 sm:px-8 max-w-[1400px] mx-auto">
      {isDashboard && isAuthenticated && (
        <div className="mb-6">
          <h1 className="text-xl font-bold text-gray-900 tracking-tight mb-1 flex items-center gap-2">
            Hello, {user?.name?.split(' ')[0] || 'User'} <span className="text-lg">👋</span>
          </h1>
          <p className="text-gray-500 text-xs">
            Find the right opportunities and build your dream career.
          </p>
        </div>
      )}

      {showBanner && isAuthenticated && isDashboard && (
        <div className="bg-[#FFF7ED] rounded-2xl p-4 sm:p-6 mb-8 flex flex-col sm:flex-row items-center justify-between border border-orange-100 shadow-sm relative overflow-hidden">
          <div className="flex items-center gap-4 relative z-10 mb-4 sm:mb-0">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shrink-0 shadow-sm text-orange-500">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-lg">Want better job recommendations?</h3>
              <p className="text-gray-600 text-sm">Complete your career preferences to get personalized job matches.</p>
            </div>
          </div>
          <div className="flex items-center gap-4 relative z-10 w-full sm:w-auto">
            <Button 
              className="w-full sm:w-auto bg-orange-600 hover:bg-orange-700 text-white rounded-xl py-5 font-semibold"
              onClick={() => router.push('/profile/preferences')}
            >
              Personalize My Jobs
            </Button>
            <button 
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              onClick={() => setShowBanner(false)}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Modern Search & Dropdown Filter System */}
      {activeTab === 'all' && (!isDashboard || isAuthenticated) && (
        <div className="mb-8 space-y-3">
          {/* Main Search Bar */}
          <form onSubmit={handleSearch} className="w-full bg-white p-1.5 border border-gray-200 rounded-2xl shadow-xs flex flex-col sm:flex-row items-stretch sm:items-center gap-1.5 sm:gap-0 divide-y sm:divide-y-0 sm:divide-x divide-gray-100">
            
            <div className="flex-1 flex items-center px-3.5 py-1.5 sm:py-2 transition-colors focus-within:bg-gray-50 rounded-t-xl sm:rounded-l-xl sm:rounded-tr-none relative">
              <Search className="w-4 h-4 text-gray-400 shrink-0" />
              <input 
                type="text"
                placeholder="Job title, skills, keywords, or company"
                className="bg-transparent border-none outline-none text-sm font-medium text-gray-800 w-full ml-2.5 placeholder:text-gray-400 focus:ring-0"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => {
                  if (query.length >= 2 && suggestions.length > 0) setShowSuggestions(true);
                }}
                onBlur={() => {
                  setTimeout(() => setShowSuggestions(false), 200);
                }}
              />
              
              {showSuggestions && (
                <div className="absolute top-full left-0 w-full mt-2 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden z-50 max-h-80 overflow-y-auto">
                  {isSearching ? (
                    <div className="p-4 text-center text-sm text-gray-500 animate-pulse">Searching...</div>
                  ) : suggestions.length === 0 ? (
                    <div className="p-4 text-center text-sm text-gray-500">No suggestions found</div>
                  ) : (
                    <div className="flex flex-col py-2">
                      {suggestions.map((s, idx) => (
                        <div 
                          key={`${s.type}-${s.id}-${idx}`} 
                          className="px-4 py-3 hover:bg-gray-50 cursor-pointer flex items-center gap-3 border-b border-gray-50 last:border-0"
                          onClick={() => {
                            if (s.type === 'company') {
                              router.push(`/companies/${s.id}`);
                            } else {
                              router.push(`/jobs/${s.id}`);
                            }
                          }}
                        >
                          <div className="w-8 h-8 rounded-md bg-orange-50 flex items-center justify-center shrink-0">
                            {s.type === 'company' ? <Building2 className="w-4 h-4 text-orange-600" /> : <Briefcase className="w-4 h-4 text-orange-600" />}
                          </div>
                          <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-900 line-clamp-1">{s.text}</span>
                            {s.subtext && <span className="text-xs text-gray-500 line-clamp-1">{s.subtext}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="flex-1 flex items-center px-3.5 py-1.5 sm:py-2 transition-colors focus-within:bg-gray-50">
              <MapPin className="w-4 h-4 text-gray-400 shrink-0" />
              <input 
                type="text"
                placeholder="Location (e.g. Pune, Bengaluru, Mumbai)"
                className="bg-transparent border-none outline-none text-sm font-medium text-gray-800 w-full ml-2.5 placeholder:text-gray-400 focus:ring-0"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
            
            <div className="px-1.5 py-1.5 sm:py-0 sm:pr-1.5 sm:pl-3">
              <Button type="submit" className="w-full sm:w-auto rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold shadow-xs px-6 py-2.5 h-auto text-xs sm:text-sm transition-transform active:scale-95">
                Search Jobs
              </Button>
            </div>
          </form>

          {/* Dedicated Filter Dropdowns Row */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Location Filter Dropdown */}
            <div className="relative min-w-[150px] flex-1 sm:flex-initial">
              <select 
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">📍 All Locations (India)</option>
                <option value="Bengaluru">Bengaluru</option>
                <option value="Pune">Pune</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Chennai">Chennai</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Noida">Noida / Delhi NCR</option>
                <option value="Kolkata">Kolkata</option>
                <option value="Kochi">Kochi</option>
                <option value="Gandhinagar">Gandhinagar / Gujarat</option>
                <option value="Nagpur">Nagpur</option>
                <option value="Bhopal">Bhopal / MP</option>
                <option value="Pan India">Pan India</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400 absolute right-3 top-3.5 pointer-events-none" />
            </div>

            {/* Domain Filter */}
            <div className="relative min-w-[170px] flex-1 sm:flex-initial">
              <select 
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">🏢 All Domains / Functions</option>
                <option value="Technology">Technology & Software</option>
                <option value="Infrastructure">IT Infrastructure & Cloud</option>
                <option value="Business Process Services">BPS & Operations</option>
                <option value="Consulting">Consulting & Enterprise (SAP/ERP)</option>
                <option value="Quality Assurance">Quality Assurance & Testing</option>
                <option value="Finance">Finance & Accounting</option>
                <option value="Human Resources">Human Resources (HR)</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400 absolute right-3 top-3.5 pointer-events-none" />
            </div>

            {/* Experience Filter */}
            <div className="relative min-w-[150px] flex-1 sm:flex-initial">
              <select 
                value={experience}
                onChange={(e) => setExperience(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">🎓 All Experience Levels</option>
                <option value="0-2">Entry Level (0 - 2 Yrs)</option>
                <option value="2-5">Mid-Level (2 - 5 Yrs)</option>
                <option value="5-8">Senior (5 - 8 Yrs)</option>
                <option value="8+">Lead / Principal (8+ Yrs)</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400 absolute right-3 top-3.5 pointer-events-none" />
            </div>

            {/* Role Filter */}
            <div className="relative min-w-[170px] flex-1 sm:flex-initial">
              <select 
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">💼 All Specializations / Roles</option>
                <option value="Engineer">Software Engineer / Dev</option>
                <option value="Data">Data & AI Engineer</option>
                <option value="Cloud">Cloud & DevOps</option>
                <option value="Consultant">Consultant / ERP Specialist</option>
                <option value="Automation">QA & Automation Engineer</option>
                <option value="Analyst">Business / Financial Analyst</option>
                <option value="Associate">Operations / Process Associate</option>
                <option value="Architect">Architect / Tech Lead</option>
                <option value="Audit">Audit Manager / Specialist</option>
                <option value="Tax">Tax Consultant / Advisor</option>
                <option value="Risk">Risk Advisory / Compliance</option>
                <option value="HR">Human Resources / Recruiter</option>
                <option value="Director">Director / Leadership</option>
                <option value="Product">Product Manager / Owner</option>
                <option value="Scrum">Scrum Master / Agile Coach</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400 absolute right-3 top-3.5 pointer-events-none" />
            </div>

            {/* Work Mode */}
            <div className="relative min-w-[130px] flex-1 sm:flex-initial">
              <select 
                value={workMode}
                onChange={(e) => setWorkMode(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">🌐 All Work Modes</option>
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="On-site">On-site</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400 absolute right-3 top-3.5 pointer-events-none" />
            </div>

            {/* Clear All Filters Button */}
            {(query || location || domain || experience || role || workMode) && (
              <button
                type="button"
                onClick={handleClearFilters}
                className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-gray-500 hover:text-orange-600 hover:bg-orange-50 rounded-xl transition-colors"
              >
                <X className="w-3.5 h-3.5" />
                Clear Filters
              </button>
            )}
          </div>
        </div>
      )}

      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            {activeTab === 'for_you' ? 'Recommended Jobs' : 'All Jobs'}
          </h2>
          <p className="text-sm text-gray-500">
            {activeTab === 'for_you' ? 'Top matches based on your profile and preferences' : 'Browse thousands of tech jobs'}
          </p>
        </div>
        <button 
          onClick={() => handleTabChange(activeTab === 'all' ? 'for_you' : 'all')}
          className="text-sm font-semibold text-orange-600 hover:text-orange-700 transition-colors"
        >
          View {activeTab === 'all' ? 'Recommended' : 'All'}
        </button>
      </div>

      {/* Content Area */}
      {loading && page === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 p-6 h-[280px] animate-pulse">
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-gray-100 rounded-full" />
                <div className="w-8 h-8 bg-gray-100 rounded-full" />
              </div>
              <div className="w-3/4 h-5 bg-gray-100 rounded mb-2" />
              <div className="w-1/2 h-4 bg-gray-100 rounded mb-6" />
              <div className="flex gap-2 mb-6">
                <div className="w-20 h-6 bg-gray-100 rounded" />
                <div className="w-20 h-6 bg-gray-100 rounded" />
              </div>
              <div className="mt-auto flex justify-between items-center pt-4 border-t border-gray-50">
                <div className="w-16 h-4 bg-gray-100 rounded" />
                <div className="w-24 h-8 bg-gray-100 rounded-lg" />
              </div>
            </div>
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">No jobs found</h3>
          <p className="text-gray-500 max-w-sm mx-auto">
            We couldn't find any jobs matching your criteria. Try adjusting your filters or search terms.
          </p>
          <Button 
            variant="outline" 
            className="mt-6 border-gray-200"
            onClick={() => {
              setQuery('');
              setLocation('');
              setWorkMode('');
              if (activeTab === 'for_you') router.push('/jobs?tab=all');
              else loadJobs(true, 'all');
            }}
          >
            Clear all filters
          </Button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {jobs.map((job, idx) => (
              <JobCard 
                key={`${job.job_id}-${idx}`} 
                job={job} 
                isForYou={activeTab === 'for_you'} 
              />
            ))}
          </div>
          
          {jobs.length >= limit && (
            <div className="mt-10 text-center">
              <Button 
                onClick={() => loadJobs(false)}
                disabled={loading}
                variant="outline"
                className="rounded-xl px-8 py-6 font-semibold border-gray-200 text-gray-700 hover:bg-gray-50"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
                    Loading more...
                  </span>
                ) : 'Load More Jobs'}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
