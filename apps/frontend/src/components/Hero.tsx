'use client';

import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

interface HeroProps {
  jobCount: number;
  companyCount: number;
}

export function Hero({ jobCount, companyCount }: HeroProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [query, setQuery] = useState('');

  // Do not show the guest Hero if the user is logged in or we are still checking auth.
  if (isLoading || isAuthenticated) {
    return null;
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/jobs?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div className="relative overflow-hidden bg-[#FDFBF7] pt-8 sm:pt-24 pb-6 sm:pb-20 border-b border-gray-100">
      {/* Decorative background blobs */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob"></div>
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-orange-100 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>

      <div className="container mx-auto px-4 relative z-10 text-center max-w-4xl">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-gray-900 mb-4 leading-tight drop-shadow-sm">
          Find the right <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-orange-400">opportunity</span> for you
        </h1>
        <p className="text-lg md:text-xl text-gray-500 mb-8 max-w-2xl mx-auto font-medium">
          Discover jobs that match your skills, career goals, and lifestyle.
        </p>
        
        <form onSubmit={handleSearch} className="max-w-3xl mx-auto relative mb-6 flex items-center group">
          <div className="absolute left-5 text-gray-400 group-focus-within:text-orange-500 transition-colors">
            <Search className="w-5 h-5" />
          </div>
          <input 
            type="text" 
            placeholder="Search by job title, skills, or companies..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full py-3.5 sm:py-4 pl-14 pr-36 bg-white/90 backdrop-blur-md border border-gray-200 rounded-full text-base shadow-lg focus:outline-none focus:ring-4 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-gray-900 placeholder:text-gray-400 font-medium"
          />
          <button 
            type="submit"
            className="absolute right-2 px-7 py-2.5 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 text-white font-bold rounded-full transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5 text-sm sm:text-base"
          >
            Search
          </button>
        </form>

        <div className="text-sm font-medium text-gray-500 flex items-center justify-center gap-2">
          <span>Popular:</span>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-white/60 border border-gray-200 rounded-full hover:border-orange-300 hover:text-orange-600 cursor-pointer transition-colors" onClick={() => router.push('/jobs?q=Frontend')}>Frontend</span>
            <span className="px-3 py-1 bg-white/60 border border-gray-200 rounded-full hover:border-orange-300 hover:text-orange-600 cursor-pointer transition-colors" onClick={() => router.push('/jobs?q=Backend')}>Backend</span>
            <span className="px-3 py-1 bg-white/60 border border-gray-200 rounded-full hover:border-orange-300 hover:text-orange-600 cursor-pointer transition-colors" onClick={() => router.push('/jobs?q=Remote')}>Remote</span>
          </div>
        </div>
      </div>
    </div>
  );
}
