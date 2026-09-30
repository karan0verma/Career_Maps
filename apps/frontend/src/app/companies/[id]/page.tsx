"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiRequest } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import { Building2, MapPin, Briefcase, ExternalLink, Search, ArrowLeft } from "lucide-react";

interface Company {
  company_id: string;
  official_name: string;
  display_name: string;
  website: string;
  career_url: string;
  industry: string;
  company_type: string;
  city: string;
  country: string;
  logo_url?: string;
  total_active_jobs?: number;
}

interface Job {
  job_id: string;
  title: string;
  location: string;
  country?: string;
  work_mode?: string;
  employment_type?: string;
  experience_level?: string;
  required_skills?: string[];
  posted_at?: string;
}

export default function CompanyDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const [company, setCompany] = useState<Company | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searchRole, setSearchRole] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("");
  const [selectedExp, setSelectedExp] = useState("");
  const [selectedRole, setSelectedRole] = useState("");

  const limit = 24;

  const loadCompany = async () => {
    try {
      const compData = await apiRequest(`/companies/${params.id}`);
      setCompany(compData);
    } catch (err) {
      console.error("Failed to load company:", err);
    }
  };

  const loadJobs = async (reset = false, overrides?: { location?: string; domain?: string; experience?: string; role?: string; search?: string }) => {
    if (!params?.id) return;
    
    if (reset) {
      setLoading(true);
      setPage(0);
    } else {
      setLoadingMore(true);
    }

    try {
      const currentPage = reset ? 0 : page;
      const skip = currentPage * limit;
      let url = `/jobs?company_id=${params.id}&skip=${skip}&limit=${limit}`;
      
      const activeSearch = overrides?.search !== undefined ? overrides.search : searchRole;
      const activeLocation = overrides?.location !== undefined ? overrides.location : selectedLocation;
      const activeDomain = overrides?.domain !== undefined ? overrides.domain : selectedDomain;
      const activeExp = overrides?.experience !== undefined ? overrides.experience : selectedExp;
      const activeRole = overrides?.role !== undefined ? overrides.role : selectedRole;

      if (activeSearch.trim()) {
        url += `&q=${encodeURIComponent(activeSearch.trim())}`;
      }
      if (activeLocation) {
        url += `&location=${encodeURIComponent(activeLocation)}`;
      }
      if (activeDomain) {
        url += `&domain=${encodeURIComponent(activeDomain)}`;
      }
      if (activeExp) {
        url += `&experience=${encodeURIComponent(activeExp)}`;
      }
      if (activeRole) {
        url += `&role=${encodeURIComponent(activeRole)}`;
      }

      const jobsData = await apiRequest(url);
      
      if (jobsData && Array.isArray(jobsData)) {
        if (reset) {
          setJobs(jobsData);
        } else {
          setJobs(prev => {
            const existing = new Set(prev.map(j => j.job_id));
            const fresh = jobsData.filter(j => !existing.has(j.job_id));
            return [...prev, ...fresh];
          });
        }
        setHasMore(jobsData.length === limit);
        setPage(currentPage + 1);
      } else {
        setHasMore(false);
      }
    } catch (err) {
      console.error("Failed to load jobs:", err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    if (params?.id) {
      loadCompany();
      loadJobs(true);
    }
  }, [params?.id, selectedLocation, selectedDomain, selectedExp, selectedRole]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadJobs(true);
  };

  const handleClearAll = () => {
    setSearchRole("");
    setSelectedLocation("");
    setSelectedDomain("");
    setSelectedExp("");
    setSelectedRole("");
    loadJobs(true, { search: "", location: "", domain: "", experience: "", role: "" });
  };

  if (loading && !company) {
    return (
      <div className="container mx-auto py-10 px-4 max-w-5xl animate-pulse">
        <div className="h-10 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-32 bg-gray-100 rounded-2xl w-full mb-8"></div>
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="space-y-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-gray-100 rounded-2xl"></div>)}
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="container mx-auto py-20 px-4 text-center">
        <h2 className="text-2xl font-bold mb-2 text-gray-900">Company Not Found</h2>
        <Button variant="outline" onClick={() => router.push("/companies")}>Back to Companies Directory</Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FDFBF7] py-10 px-4 sm:px-8">
      <div className="container mx-auto max-w-5xl">
        <Link 
          href="/companies" 
          className="inline-flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-orange-600 transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Companies
        </Link>
        
        {/* Company Header Card */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8 mb-10">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 pb-6 border-b border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-white text-orange-600 flex items-center justify-center shrink-0 border border-gray-200 overflow-hidden shadow-xs">
                {company.logo_url ? (
                  <img src={company.logo_url} alt={company.display_name} className="w-full h-full object-contain p-1.5" />
                ) : (
                  <Building2 className="w-8 h-8 text-gray-400" />
                )}
              </div>
              <div>
                <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">{company.display_name}</h1>
                <p className="text-base text-gray-500 font-medium">{company.industry || "Technology"}</p>
              </div>
            </div>
            
            {company.career_url && (
              <a 
                href={company.career_url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-orange-600 hover:bg-orange-700 text-white rounded-xl font-semibold text-sm transition-all shadow-sm"
              >
                Official Careers Portal
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-6 text-sm">
            <div>
              <p className="text-gray-400 font-medium mb-1">Headquarters</p>
              <p className="font-semibold text-gray-800">{company.city ? `${company.city}, ${company.country}` : (company.country || "Global")}</p>
            </div>
            <div>
              <p className="text-gray-400 font-medium mb-1">Company Type</p>
              <p className="font-semibold text-gray-800">{company.company_type || "Public Company"}</p>
            </div>
            <div>
              <p className="text-gray-400 font-medium mb-1">Website</p>
              {company.website ? (
                <a 
                  href={company.website.startsWith('http') ? company.website : `https://${company.website}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="font-semibold text-orange-600 hover:underline truncate block"
                >
                  {company.website.replace(/^https?:\/\//, '')}
                </a>
              ) : (
                <p className="font-semibold text-gray-800">Available on Portal</p>
              )}
            </div>
          </div>
        </div>

        {/* Roles Section Header & Search */}
        <div className="space-y-4 mb-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Open Positions</h2>
              <p className="text-sm text-gray-500 mt-0.5">
                Showing {jobs.length} of {company.total_active_jobs || jobs.length} open positions
              </p>
            </div>
            
            <form onSubmit={handleSearch} className="flex gap-2 w-full sm:w-auto">
              <div className="relative w-full sm:w-80">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={`Search ${company.display_name} roles, skills...`}
                  value={searchRole}
                  onChange={(e) => setSearchRole(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 shadow-2xs"
                />
              </div>
              <Button type="submit" className="bg-orange-600 hover:bg-orange-700 text-white rounded-xl text-sm font-semibold px-4">
                Search
              </Button>
            </form>
          </div>

          {/* Interactive Filter Dropdowns */}
          <div className="flex flex-wrap items-center gap-2.5 pt-1">
            {/* Location Filter */}
            <div className="relative min-w-[150px] flex-1 sm:flex-initial">
              <select 
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">📍 All Locations</option>
                <option value="Bengaluru">Bengaluru</option>
                <option value="Pune">Pune</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Chennai">Chennai</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Noida">Noida / Delhi NCR</option>
                <option value="Kolkata">Kolkata</option>
                <option value="Kochi">Kochi</option>
                <option value="Gandhinagar">Gandhinagar</option>
                <option value="Nagpur">Nagpur</option>
                <option value="Bhopal">Bhopal</option>
                <option value="Pan India">Pan India</option>
              </select>
            </div>

            {/* Domain Filter */}
            <div className="relative min-w-[170px] flex-1 sm:flex-initial">
              <select 
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
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
            </div>

            {/* Experience Filter */}
            <div className="relative min-w-[150px] flex-1 sm:flex-initial">
              <select 
                value={selectedExp}
                onChange={(e) => setSelectedExp(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">🎓 All Experience Levels</option>
                <option value="0-2">Entry Level (0 - 2 Yrs)</option>
                <option value="2-5">Mid-Level (2 - 5 Yrs)</option>
                <option value="5-8">Senior (5 - 8 Yrs)</option>
                <option value="8+">Lead / Principal (8+ Yrs)</option>
              </select>
            </div>

            {/* Role Filter */}
            <div className="relative min-w-[170px] flex-1 sm:flex-initial">
              <select 
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full appearance-none bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-xl pl-3.5 pr-8 py-2.5 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 cursor-pointer shadow-2xs transition-all"
              >
                <option value="">💼 All Specializations</option>
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
            </div>

            {/* Clear All Filters */}
            {(searchRole || selectedLocation || selectedDomain || selectedExp || selectedRole) && (
              <button
                type="button"
                onClick={handleClearAll}
                className="text-xs font-semibold text-gray-500 hover:text-orange-600 hover:bg-orange-50 px-3 py-2 rounded-xl transition-colors"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Jobs List */}
        {jobs.length === 0 && !loading ? (
          <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm">
            <p className="text-gray-500 text-base font-medium">No open positions matching your filter criteria.</p>
            {(searchRole || selectedLocation || selectedDomain || selectedExp || selectedRole) && (
              <Button 
                variant="outline" 
                onClick={handleClearAll}
                className="mt-4 rounded-xl"
              >
                Reset Filters
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job, idx) => (
              <Link key={`${job.job_id}-${idx}`} href={`/jobs/${job.job_id}`}>
                <div className="bg-white rounded-2xl border border-gray-200 hover:border-orange-200 hover:shadow-md transition-all p-6 cursor-pointer flex flex-col sm:flex-row justify-between sm:items-center gap-4">
                  <div>
                    <h3 className="font-bold text-lg text-gray-900 hover:text-orange-600 transition-colors">{job.title}</h3>
                    
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-gray-500 mt-2 font-medium">
                      {job.location && (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-gray-400" />
                          {job.location}
                        </span>
                      )}
                      {job.work_mode && (
                        <span className="flex items-center gap-1">
                          <Briefcase className="w-3.5 h-3.5 text-gray-400" />
                          {job.work_mode}
                        </span>
                      )}
                      {job.experience_level && (
                        <span className="px-2 py-0.5 bg-orange-50 text-orange-700 rounded-md font-semibold">
                          {job.experience_level}
                        </span>
                      )}
                    </div>

                    {job.required_skills && job.required_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {job.required_skills.slice(0, 3).map((s, idx) => (
                          <span key={idx} className="px-2.5 py-0.5 bg-gray-50 border border-gray-100 text-gray-600 rounded-md text-xs font-medium">
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-sm font-bold text-orange-600 hover:text-orange-700 flex items-center gap-1">
                      View Details &rarr;
                    </span>
                  </div>
                </div>
              </Link>
            ))}
            
            {/* Load More Button */}
            {hasMore && (
              <div className="pt-6 text-center">
                <Button
                  onClick={() => loadJobs(false)}
                  disabled={loadingMore}
                  variant="outline"
                  className="rounded-xl px-8 py-5 font-semibold border-gray-200 text-gray-700 hover:bg-gray-50 shadow-sm"
                >
                  {loadingMore ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
                      Loading more roles...
                    </span>
                  ) : (
                    `Load More Positions (${jobs.length} of ${company.total_active_jobs || jobs.length})`
                  )}
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
