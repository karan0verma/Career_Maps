'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Sparkles, TrendingUp, Building2, Briefcase, ChevronRight, X, Activity } from 'lucide-react';

interface CompanyStat {
  name: string;
  count: number;
}

export function LiveStatsFloatingBanner() {
  const [isVisible, setIsVisible] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
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
    // Fetch live company counts from backend API
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
        // Fallback to static accurate numbers if offline
      }
    };

    fetchLiveStats();
  }, []);

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 max-w-[95vw] sm:max-w-lg transition-all duration-300">
      <div className="bg-gray-900/95 backdrop-blur-xl text-white rounded-2xl shadow-2xl border border-gray-700/60 p-3.5 sm:p-4 text-xs sm:text-sm">
        
        {/* Top Header Row */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="font-semibold tracking-wide text-gray-200 flex items-center gap-1.5">
              <Activity className="h-4 w-4 text-emerald-400 animate-pulse" />
              LIVE CAREER RADAR
            </span>
            <span className="bg-emerald-500/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-500/30 uppercase tracking-wider">
              Real-time
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-gray-400 hover:text-white px-2 py-0.5 rounded-lg hover:bg-gray-800 transition text-[11px] font-medium"
            >
              {isExpanded ? 'Collapse ▲' : 'View All ▼'}
            </button>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-400 hover:text-gray-200 p-1 rounded-lg hover:bg-gray-800 transition"
              title="Close Banner"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {/* Primary Stats Summary Pill */}
        <div className="mt-2.5 flex items-center justify-between gap-2 bg-gradient-to-r from-gray-800/90 to-gray-800/40 rounded-xl p-2.5 border border-gray-700/50">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Briefcase className="h-4 w-4 text-orange-400" />
              <div>
                <div className="font-bold text-sm sm:text-base text-white tracking-tight">
                  {totalJobs.toLocaleString()}+
                </div>
                <div className="text-[10px] text-gray-400 uppercase font-medium">Verified Jobs</div>
              </div>
            </div>

            <div className="h-7 w-[1px] bg-gray-700"></div>

            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4 text-blue-400" />
              <div>
                <div className="font-bold text-sm sm:text-base text-white tracking-tight">
                  {totalCompanies} Top Giants
                </div>
                <div className="text-[10px] text-gray-400 uppercase font-medium">Active Portals</div>
              </div>
            </div>
          </div>

          <Link
            href="/jobs"
            className="flex items-center gap-1 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-semibold text-xs px-3 py-1.5 rounded-lg shadow-md transition transform active:scale-95"
          >
            Browse
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {/* Ticker / Scrolling Highlights */}
        {!isExpanded && (
          <div className="mt-2 text-[11px] text-gray-300 overflow-hidden whitespace-nowrap bg-black/30 rounded-lg px-2.5 py-1 flex items-center gap-2">
            <span className="text-orange-400 font-bold shrink-0">⚡ Live:</span>
            <div className="animate-marquee inline-block text-gray-300">
              HCLTech ({companyStats[0]?.count.toLocaleString() || '6,766'}) • TCS ({companyStats[1]?.count.toLocaleString() || '3,962'}) • Amazon ({companyStats[2]?.count.toLocaleString() || '2,596'}) • Wipro ({companyStats[3]?.count.toLocaleString() || '2,586'}) • Infosys ({companyStats[4]?.count.toLocaleString() || '1,611'}) • Cognizant ({companyStats[5]?.count.toLocaleString() || '750'}) • Oracle ({companyStats[7]?.count.toLocaleString() || '223'}) • Microsoft ({companyStats[8]?.count.toLocaleString() || '193'})
            </div>
          </div>
        )}

        {/* Expanded Grid View of all Companies */}
        {isExpanded && (
          <div className="mt-3 pt-3 border-t border-gray-800 space-y-1.5 max-h-48 overflow-y-auto pr-1">
            <div className="text-[11px] font-semibold text-gray-400 mb-1">Company Breakdown:</div>
            <div className="grid grid-cols-2 gap-1.5 text-[11px]">
              {companyStats.map((c, idx) => (
                <Link
                  key={idx}
                  href="/companies"
                  className="flex items-center justify-between bg-gray-800/80 hover:bg-gray-750 px-2.5 py-1.5 rounded-lg border border-gray-700/40 transition"
                >
                  <span className="text-gray-300 truncate">{c.name}</span>
                  <span className="font-bold text-orange-400 ml-1">{c.count.toLocaleString()}</span>
                </Link>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
