'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Activity, Briefcase, Building2, ChevronRight, Sparkles, Zap } from 'lucide-react';

interface CompanyStat {
  name: string;
  count: number;
}

export function LiveTickerFullWidthBanner() {
  const [totalJobs, setTotalJobs] = useState<number>(19434);
  const [totalCompanies, setTotalCompanies] = useState<number>(10);
  const [companyStats, setCompanyStats] = useState<CompanyStat[]>([
    { name: 'HCLTech', count: 6766 },
    { name: 'TCS', count: 3962 },
    { name: 'Amazon', count: 2596 },
    { name: 'Wipro', count: 2586 },
    { name: 'Infosys', count: 1611 },
    { name: 'Cognizant', count: 750 },
    { name: 'Tech Mahindra', count: 645 },
    { name: 'Oracle', count: 223 },
    { name: 'Microsoft', count: 193 },
    { name: 'Coforge', count: 102 },
  ]);

  useEffect(() => {
    const fetchLiveStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/companies');
        if (res.ok) {
          const comps = await res.json();
          if (Array.isArray(comps) && comps.length > 0) {
            setTotalCompanies(comps.length);
            let sum = 0;
            const stats: CompanyStat[] = comps.map((c: any) => {
              const count = c.total_active_jobs || c.job_count || 0;
              sum += count;
              return {
                name: c.display_name || c.official_name,
                count: count,
              };
            });
            if (sum > 0) {
              setTotalJobs(sum);
              setCompanyStats(stats.sort((a, b) => b.count - a.count));
            }
          }
        }
      } catch (err) {
        // Fallback to static numbers if API unreachable
      }
    };

    fetchLiveStats();
  }, []);

  return (
    <div className="w-full mb-6 overflow-hidden rounded-2xl bg-gradient-to-r from-orange-950/95 via-slate-900 to-amber-950/90 text-white border border-orange-500/30 shadow-xl shadow-orange-950/20 relative group backdrop-blur-md">
      
      {/* Dynamic Ambient Background Glows */}
      <div className="absolute -left-12 top-0 w-40 h-full bg-orange-500/20 blur-2xl pointer-events-none"></div>
      <div className="absolute -right-12 top-0 w-40 h-full bg-amber-500/20 blur-2xl pointer-events-none"></div>
      <div className="absolute left-1/2 -top-10 w-48 h-20 bg-emerald-500/10 blur-2xl pointer-events-none"></div>

      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 p-3 sm:px-5 sm:py-2.5 relative z-10">
        
        {/* Left Badge / Currently Active Section */}
        <div className="flex items-center gap-3 shrink-0 border-b md:border-b-0 md:border-r border-orange-500/20 pb-2 md:pb-0 md:pr-4">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 shadow-sm shadow-emerald-400"></span>
          </span>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-500/30">
              <Zap className="h-3 w-3 text-emerald-400 fill-emerald-400 animate-pulse" />
              CURRENTLY ACTIVE
            </span>
            <span className="h-3 w-[1px] bg-gray-700"></span>
            <span className="text-xs sm:text-sm font-extrabold text-amber-300 tracking-tight">
              {totalJobs.toLocaleString()}+ Jobs
            </span>
            <span className="text-[11px] text-gray-300 hidden lg:inline font-medium">
              ({totalCompanies} Companies)
            </span>
          </div>
        </div>

        {/* Continuous Streaming Ticker (One End to Other End) */}
        <div className="flex-1 overflow-hidden relative flex items-center min-w-0 mx-1">
          <div className="animate-marquee whitespace-nowrap flex items-center gap-6 text-xs text-gray-200 font-medium py-0.5">
            {companyStats.map((c, idx) => (
              <Link
                key={idx}
                href="/companies"
                className="inline-flex items-center gap-1.5 hover:text-amber-300 transition bg-white/5 hover:bg-white/10 px-2.5 py-1 rounded-lg border border-white/5 hover:border-amber-400/30"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                <span className="text-gray-100 font-semibold">{c.name}:</span>
                <span className="text-amber-400 font-bold">{c.count.toLocaleString()}</span>
              </Link>
            ))}
            <span className="text-gray-600 font-normal">|</span>
            <span className="text-emerald-400 inline-flex items-center gap-1 font-semibold">
              <Sparkles className="h-3 w-3 text-emerald-400" /> Precision Delta Sync Live
            </span>
            <span className="text-gray-600 font-normal">|</span>
          </div>
        </div>

        {/* Right Action Button */}
        <div className="shrink-0 flex items-center justify-end">
          <Link
            href="/jobs"
            className="inline-flex items-center gap-1.5 bg-gradient-to-r from-orange-500 via-amber-500 to-orange-600 hover:from-orange-600 hover:to-amber-600 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl shadow-md shadow-orange-950/40 transition transform hover:-translate-y-0.5 active:scale-95 whitespace-nowrap border border-orange-400/30"
          >
            Browse All
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>

      </div>
    </div>
  );
}
