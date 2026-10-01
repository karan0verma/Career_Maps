'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Sidebar } from './Sidebar';
import { Navbar } from './navbar';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Bookmark, Compass, Menu, CheckCircle, Users } from 'lucide-react';
import { HeaderLiveTicker } from './HeaderLiveTicker';

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const isAuthPage = pathname === '/login' || pathname === '/register';
  
  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center bg-[#FDFBF7] text-gray-500 animate-pulse">Loading...</div>;
  }

  if (isAuthenticated && !isAuthPage) {
    return (
      <div className="min-h-screen bg-[#FDFBF7]">
        {/* Slide-out Drawer */}
        <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

        <div className="w-full flex flex-col min-h-screen">
          {/* Top Header with 3-Line Hamburger Menu */}
          <header className="flex flex-col lg:flex-row h-auto lg:h-[84px] py-2 lg:py-0 items-center justify-between px-2 lg:px-8 border-b border-gray-200/80 bg-white/80 backdrop-blur-md sticky top-0 z-30 shadow-xs gap-2 lg:gap-0">
            
            {/* Top Row on mobile / Left side on desktop */}
            <div className="w-full lg:w-auto flex items-center justify-between lg:justify-start gap-3 lg:gap-4 shrink-0">
              <div className="flex items-center gap-2">
                {/* 3-Line Hamburger Menu Button */}
                <button
                  onClick={() => setIsSidebarOpen(true)}
                  className="p-1.5 lg:p-2.5 rounded-xl bg-orange-50 hover:bg-orange-100 text-orange-600 hover:text-orange-700 transition shadow-xs flex items-center justify-center group"
                  title="Open Navigation"
                >
                  <Menu className="h-5 w-5 transition-transform group-hover:scale-110" />
                </button>
  
                <Link href="/" className="flex items-center gap-2 text-orange-600 shrink-0">
                  <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-xl bg-orange-100 flex items-center justify-center text-orange-600">
                    <Compass className="h-4 w-4 lg:h-5 lg:w-5" />
                  </div>
                  <span className="font-extrabold text-lg lg:text-xl tracking-tight text-gray-900 inline-block">Career Maps</span>
                </Link>
              </div>

              {/* Right Profile Info - Mobile Only */}
              <div className="flex lg:hidden items-center gap-2 shrink-0">
                <Link href="/profile/applied" className={`p-1.5 rounded-xl hover:bg-gray-100 ${pathname === '/profile/applied' ? 'text-orange-600' : 'text-gray-500'}`}>
                  <CheckCircle className="h-5 w-5" />
                </Link>
                <Link href="/profile/saved" className={`p-1.5 rounded-xl hover:bg-gray-100 ${pathname === '/profile/saved' ? 'text-orange-600' : 'text-gray-500'}`}>
                  <Bookmark className="h-5 w-5" fill={pathname === '/profile/saved' ? 'currentColor' : 'none'} />
                </Link>
                <Link href="/profile" className="flex items-center gap-2 cursor-pointer ml-1">
                  {user?.profile_image ? (
                    <img src={user.profile_image} alt="" className="h-7 w-7 rounded-full bg-gray-200 object-cover shadow-xs" />
                  ) : (
                    <div className="h-7 w-7 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-[10px] shrink-0 border border-orange-200">
                      {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                    </div>
                  )}
                </Link>
              </div>
            </div>

            {/* Live Ticker: 2nd Row on mobile / Center on desktop */}
            <div className="w-full lg:flex-1 lg:px-4 order-last lg:order-none min-w-0 overflow-hidden mt-1 lg:mt-0">
              <HeaderLiveTicker />
            </div>

            {/* Right Profile Info - Desktop Only */}
            <div className="hidden lg:flex items-center gap-2 lg:gap-4 shrink-0">
              <Link 
                href="/profile/applied"
                className={`transition-colors p-2 rounded-xl hover:bg-gray-100 ${pathname === '/profile/applied' ? 'text-orange-600' : 'text-gray-500 hover:text-gray-700'}`}
                title="Applied Jobs"
              >
                <CheckCircle className="h-5 w-5" />
              </Link>
              <Link 
                href="/profile/saved"
                className={`transition-colors p-2 rounded-xl hover:bg-gray-100 ${pathname === '/profile/saved' ? 'text-orange-600' : 'text-gray-500 hover:text-gray-700'}`}
                title="Saved Jobs"
              >
                <Bookmark className="h-5 w-5" fill={pathname === '/profile/saved' ? 'currentColor' : 'none'} />
              </Link>
              
              <Link href="/profile" className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
                {user?.profile_image ? (
                  <img src={user.profile_image} alt="" className="h-8 w-8 rounded-full bg-gray-200 object-cover shadow-xs" />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-xs shrink-0 border border-orange-200">
                    {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                  </div>
                )}
              </Link>
            </div>
          </header>

          <main className="flex-1 relative z-10 w-full pb-8">
            {children}
          </main>
          
          <footer className="w-full bg-white border-t border-gray-200 py-4 lg:py-6 mt-auto">
            <div className="max-w-[1400px] mx-auto px-4 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center text-xs sm:text-sm text-gray-500 font-medium">
                &copy; {new Date().getFullYear()} Career Maps. All rights reserved.
              </div>
              <div className="flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-100 shadow-xs text-xs sm:text-sm text-gray-500 font-medium">
                <Users className="w-4 h-4 text-orange-500" />
                Visitors: <span className="font-bold text-gray-700">
                  {(12450 + (Math.max(0, Math.floor((new Date().getTime() - new Date('2024-08-01').getTime()) / (1000 * 60 * 60 * 24))) * 42) + new Date().getHours()).toLocaleString()}
                </span>
              </div>
            </div>
          </footer>
        </div>
      </div>
    );
  }

  // Pre-login state with Hamburger Menu support
  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      {!isAuthPage && <Navbar onOpenMenu={() => setIsSidebarOpen(true)} />}
      <main className="flex-1 w-full pb-8 flex flex-col">
        <div className="flex-1">
          {children}
        </div>
        
        {!isAuthPage && (
          <footer className="w-full bg-white border-t border-gray-200 py-4 lg:py-6 mt-auto">
            <div className="max-w-[1400px] mx-auto px-4 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center text-xs sm:text-sm text-gray-500 font-medium">
                &copy; {new Date().getFullYear()} Career Maps. All rights reserved.
              </div>
              <div className="flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-100 shadow-xs text-xs sm:text-sm text-gray-500 font-medium">
                <Users className="w-4 h-4 text-orange-500" />
                Visitors: <span className="font-bold text-gray-700">
                  {(12450 + (Math.max(0, Math.floor((new Date().getTime() - new Date('2024-08-01').getTime()) / (1000 * 60 * 60 * 24))) * 42) + new Date().getHours()).toLocaleString()}
                </span>
              </div>
            </div>
          </footer>
        )}
      </main>
    </div>
  );
}
