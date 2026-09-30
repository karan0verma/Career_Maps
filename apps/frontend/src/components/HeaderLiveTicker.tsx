'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface CompanyStat {
  name: string;
  count: number;
}

export function HeaderLiveTicker() {
  const [totalJobs, setTotalJobs] = useState<number>(20618);
  const [totalCompanies, setTotalCompanies] = useState<number>(12);
  const [companyStats, setCompanyStats] = useState<CompanyStat[]>([
    { name: 'HCLTech', count: 6766 },
    { name: 'TCS', count: 3998 },
    { name: 'Amazon', count: 2596 },
    { name: 'Wipro', count: 2586 },
    { name: 'Infosys', count: 1611 },
    { name: 'Capgemini', count: 988 },
    { name: 'Cognizant', count: 750 },
    { name: 'Tech Mahindra', count: 703 },
    { name: 'Oracle', count: 223 },
    { name: 'Microsoft', count: 193 },
    { name: 'Adobe', count: 102 },
    { name: 'Coforge', count: 102 },
  ]);

  useEffect(() => {
    const fetchLiveStats = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/companies`);
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
        // Keep initial values if API unreachable
      }
    };

    fetchLiveStats();
  }, []);

  return (
    <div className="flex-1 w-full max-w-5xl lg:max-w-6xl mx-1 sm:mx-4 md:mx-6 overflow-hidden rounded-xl sm:rounded-2xl bg-gradient-to-r from-orange-950/95 via-slate-900 to-amber-950/95 text-white border border-orange-500/40 shadow-lg shadow-orange-950/20 h-10 sm:h-12 flex items-center px-2 sm:px-4 backdrop-blur-md">
      {/* Left Static Badge with Pulsing Emerald Dot */}
      <div className="flex items-center gap-1.5 sm:gap-2 shrink-0 pr-2 sm:pr-4 border-r border-orange-500/30">
        <span className="relative flex h-2 w-2 sm:h-2.5 sm:w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 sm:h-2.5 sm:w-2.5 bg-emerald-500"></span>
        </span>
        <span className="hidden md:inline-block font-extrabold text-[10px] sm:text-xs text-orange-300 tracking-wider uppercase whitespace-nowrap">
          CURRENTLY ACTIVE:
        </span>
        <span className="font-black text-[11px] sm:text-sm text-white whitespace-nowrap">
          {totalJobs.toLocaleString()}+ Jobs
        </span>
        <span className="text-xs text-gray-400 font-medium hidden xl:inline-block">
          ({totalCompanies} Companies)
        </span>
      </div>

      {/* Ultra Smooth, Slow Continuous Streaming Marquee Ticker */}
      <div className="flex-1 overflow-hidden relative ml-2 sm:ml-4 min-w-0">
        <div className="animate-marquee items-center gap-4 sm:gap-6 min-w-min">
          {companyStats.map((comp, idx) => (
            <span key={`ticker-1-${idx}`} className="inline-flex items-center gap-1 sm:gap-1.5 text-[10px] sm:text-[13px] text-gray-200 font-medium shrink-0">
              <span className="text-orange-400">⚡</span>
              <span className="font-semibold text-white">{comp.name}:</span>
              <span className="text-orange-400 font-bold">{comp.count.toLocaleString()}</span>
            </span>
          ))}
          {/* Duplicate set for 100% seamless infinite loop */}
          {companyStats.map((comp, idx) => (
            <span key={`ticker-2-${idx}`} className="inline-flex items-center gap-1 sm:gap-1.5 text-[10px] sm:text-[13px] text-gray-200 font-medium shrink-0">
              <span className="text-orange-400">⚡</span>
              <span className="font-semibold text-white">{comp.name}:</span>
              <span className="text-orange-400 font-bold">{comp.count.toLocaleString()}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
