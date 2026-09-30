'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Sidebar } from './Sidebar';
import { Navbar } from './navbar';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Bookmark, Compass, Menu } from 'lucide-react';
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
          <header className="flex flex-col py-2 px-2 sm:px-6 sm:py-3 border-b border-gray-200/80 bg-white/80 backdrop-blur-md sticky top-0 z-30 shadow-xs gap-2">
            
            {/* Top Row: Logo and Profile */}
            <div className="w-full flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2 sm:gap-4">
                {/* 3-Line Hamburger Menu Button */}
                <button
                  onClick={() => setIsSidebarOpen(true)}
                  className="p-1.5 sm:p-2.5 rounded-xl bg-orange-50 hover:bg-orange-100 text-orange-600 hover:text-orange-700 transition shadow-xs flex items-center justify-center group"
                  title="Open Navigation"
                >
                  <Menu className="h-5 w-5 transition-transform group-hover:scale-110" />
                </button>
  
                <Link href="/" className="flex items-center gap-2 text-orange-600 shrink-0">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-orange-100 flex items-center justify-center text-orange-600">
                    <Compass className="h-4 w-4 sm:h-5 sm:w-5" />
                  </div>
                  <span className="font-extrabold text-lg sm:text-xl tracking-tight text-gray-900 hidden sm:inline-block">Career Maps</span>
                </Link>
              </div>

              {/* Right Profile Info */}
              <div className="flex items-center gap-3 sm:gap-4 shrink-0">
                <Link 
                  href="/profile/saved"
                  className={`transition-colors p-1.5 sm:p-2 rounded-xl hover:bg-gray-100 ${pathname === '/profile/saved' ? 'text-orange-600' : 'text-gray-500 hover:text-gray-700'}`}
                  title="Saved Jobs"
                >
                  <Bookmark className="h-5 w-5" fill={pathname === '/profile/saved' ? 'currentColor' : 'none'} />
                </Link>
                
                <Link href="/profile" className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity">
                  {user?.profile_image ? (
                    <img src={user.profile_image} alt="" className="h-7 w-7 sm:h-8 sm:w-8 rounded-full bg-gray-200 object-cover shadow-xs" />
                  ) : (
                    <div className="h-7 w-7 sm:h-8 sm:w-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-[10px] sm:text-xs shrink-0 border border-orange-200">
                      {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                    </div>
                  )}
                </Link>
              </div>
            </div>

            {/* Live Ticker in Center of Header - Full width on all devices */}
            <div className="w-full min-w-0 overflow-hidden">
              <HeaderLiveTicker />
            </div>
          </header>

          <main className="flex-1 relative z-10 w-full">
            {children}
          </main>
        </div>
      </div>
    );
  }

  // Pre-login state with Hamburger Menu support
  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      {!isAuthPage && <Navbar onOpenMenu={() => setIsSidebarOpen(true)} />}
      <main className="flex-1 w-full">
        {children}
      </main>
    </div>
  );
}
