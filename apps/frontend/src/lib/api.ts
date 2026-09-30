export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Company {
  company_id: string;
  official_name: string;
  display_name: string;
  website: string;
  city?: string;
  country?: string;
  industry?: string;
  company_type?: string;
  career_url?: string;
  logo_url?: string;
  description?: string;
  total_active_jobs?: number;
}

export interface Job {
  job_id: string;
  company_id: string;
  external_job_id: string;
  title: string;
  department?: string;
  location?: string;
  city?: string;
  state?: string;
  country?: string;
  work_mode?: string;
  employment_type?: string;
  experience_level?: string;
  requirements?: string;
  required_skills?: string[];
  description?: string;
  apply_url: string;
  source_url?: string;
  posted_at?: string;
  is_active: boolean;
  first_seen_at: string;
  last_seen_at: string;
  company: Company;
  match_percentage?: number;
  match_reasons?: string[];
}

export interface Stats {
  companies: number;
  jobs: number;
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE_URL}/stats`, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchJobs(params: {
  skip?: number;
  limit?: number;
  q?: string;
  location?: string;
  work_mode?: string;
  domain?: string;
  experience?: string;
  role?: string;
  company_id?: string;
  company_type?: string;
}): Promise<Job[]> {
  const url = new URL(`${API_BASE_URL}/jobs`);
  if (params.skip) url.searchParams.append('skip', params.skip.toString());
  if (params.limit) url.searchParams.append('limit', params.limit.toString());
  if (params.q) url.searchParams.append('q', params.q);
  if (params.location) url.searchParams.append('location', params.location);
  if (params.work_mode) url.searchParams.append('work_mode', params.work_mode);
  if (params.domain) url.searchParams.append('domain', params.domain);
  if (params.experience) url.searchParams.append('experience', params.experience);
  if (params.role) url.searchParams.append('role', params.role);
  if (params.company_id) url.searchParams.append('company_id', params.company_id);
  if (params.company_type) url.searchParams.append('company_type', params.company_type);

  const res = await fetch(url.toString(), { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return res.json();
}

export async function fetchRecommendedJobs(skip: number = 0, limit: number = 24): Promise<Job[]> {
  return apiRequest(`/jobs/recommended?skip=${skip}&limit=${limit}`);
}

export async function fetchJobById(id: string): Promise<Job> {
  const res = await fetch(`${API_BASE_URL}/jobs/${id}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch job');
  return res.json();
}

export async function fetchCompanies(params?: { search?: string; limit?: number; skip?: number }): Promise<Company[]> {
  const url = new URL(`${API_BASE_URL}/companies`);
  if (params?.search) url.searchParams.append('search', params.search);
  if (params?.limit) url.searchParams.append('limit', params.limit.toString());
  if (params?.skip) url.searchParams.append('skip', params.skip.toString());
  
  const res = await fetch(url.toString(), { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch companies');
  return res.json();
}

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  // Only add auth header if running in browser
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const contentType = res.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');
  
  let data = null;
  if (isJson) {
    data = await res.json();
  }

  if (!res.ok) {
    throw new Error((data && data.detail) || `API error: ${res.statusText}`);
  }

  return data;
}
