"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchCompanies, Company } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Building2, Search, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { LiveTickerFullWidthBanner } from "@/components/LiveTickerFullWidthBanner";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  
  // Autocomplete state
  interface Suggestion {
    id: string;
    text: string;
    subtext?: string;
  }
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const router = useRouter();

  const loadCompanies = async (query: string = "") => {
    setLoading(true);
    try {
      const data = await fetchCompanies({ search: query });
      setCompanies(data || []);
    } catch (err) {
      console.error("Failed to load companies:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCompanies();
  }, []);

  // Autocomplete effect
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (search.length >= 2) {
        setIsSearching(true);
        try {
          const compsRes = await fetchCompanies({ search });
          const newSuggestions: Suggestion[] = [];
          
          if (compsRes && compsRes.length > 0) {
            // Limit to 5 suggestions
            compsRes.slice(0, 5).forEach((c: any) => {
              newSuggestions.push({
                id: c.company_id,
                text: c.display_name,
                subtext: c.industry
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
  }, [search]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    loadCompanies(search);
  };

  return (
    <div className="py-6 px-4 sm:px-8 max-w-[1400px] mx-auto min-h-screen bg-[#FDFBF7]">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Companies</h1>
          <p className="text-gray-500 mt-1">Discover top tech companies and explore open roles.</p>
        </div>
        
        <form onSubmit={handleSearch} className="flex w-full md:w-auto relative group z-20">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400 z-10" />
            <input 
              type="text" 
              placeholder="Search companies..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onFocus={() => {
                if (search.length >= 2 && suggestions.length > 0) setShowSuggestions(true);
              }}
              onBlur={() => {
                setTimeout(() => setShowSuggestions(false), 200);
              }}
              className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-l-full text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 shadow-sm relative z-10"
            />
            
            {showSuggestions && (
              <div className="absolute top-full left-0 w-full mt-2 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-50">
                {isSearching ? (
                  <div className="p-4 text-center text-sm text-gray-500 animate-pulse">Searching...</div>
                ) : suggestions.length === 0 ? (
                  <div className="p-4 text-center text-sm text-gray-500">No companies found</div>
                ) : (
                  <div className="flex flex-col py-2">
                    {suggestions.map((s, idx) => (
                      <div 
                        key={`comp-${s.id}-${idx}`} 
                        className="px-4 py-3 hover:bg-gray-50 cursor-pointer flex items-center gap-3 border-b border-gray-50 last:border-0"
                        onClick={() => {
                          router.push(`/companies/${s.id}`);
                        }}
                      >
                        <div className="w-8 h-8 rounded-md bg-orange-50 flex items-center justify-center shrink-0">
                          <Building2 className="w-4 h-4 text-orange-600" />
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
          <button type="submit" className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-r-full font-semibold transition-colors shadow-sm relative z-10">
            Search
          </button>
        </form>
      </div>


      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-48 rounded-2xl bg-gray-100 animate-pulse border border-gray-200" />
          ))}
        </div>
      ) : companies.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-medium text-gray-900">No companies found</h3>
          <p className="text-gray-500 mt-1">Try adjusting your search criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((company) => (
            <Link key={company.company_id} href={`/companies/${company.company_id}`} className="group">
              <div className="flex flex-col h-full bg-white rounded-2xl border border-gray-200 shadow-sm transition-all hover:shadow-md hover:border-orange-200 p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-white text-orange-600 flex items-center justify-center shrink-0 border border-gray-200 overflow-hidden shadow-2xs">
                    {company.logo_url ? (
                      <img src={company.logo_url} alt={company.display_name} className="w-full h-full object-contain p-1" />
                    ) : (
                      <Building2 className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                  <div>
                    <h2 className="font-bold text-lg text-gray-900 group-hover:text-orange-600 transition-colors">{company.display_name}</h2>
                    <p className="text-sm text-gray-500 truncate">{company.industry || "Technology"}</p>
                  </div>
                </div>
                
                <div className="mt-auto pt-4 flex items-center justify-between border-t border-gray-100">
                   <div className="text-xs font-bold text-orange-600 bg-orange-50 px-2.5 py-1 rounded-lg border border-orange-100">
                     {company.total_active_jobs !== undefined ? `${company.total_active_jobs} Open Positions` : "View Open Roles"}
                   </div>
                   <div className="flex items-center text-sm font-bold text-gray-700 group-hover:text-orange-600 transition-colors">
                     View <ArrowRight className="w-4 h-4 ml-1" />
                   </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
