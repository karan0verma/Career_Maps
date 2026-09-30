'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { 
  LayoutDashboard, 
  Briefcase, 
  Sparkles, 
  Bookmark, 
  UserCircle, 
  Settings2, 
  FileText, 
  X,
  Compass,
  Building2,
  Landmark,
  LogOut,
  ChevronRight
} from 'lucide-react';
import { Button } from './ui/button';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'All Jobs', href: '/jobs', icon: Briefcase },
    { name: 'Companies', href: '/companies', icon: Building2 },
    { name: 'For You', href: '/jobs?tab=for_you', icon: Sparkles },
    { name: 'Saved Jobs', href: '/profile/saved', icon: Bookmark },
    { name: 'Personalize / Preferences', href: '/profile/preferences', icon: Settings2 },
    { name: 'My Profile', href: '/profile', icon: UserCircle },
    { name: 'Resume', href: '/profile/preferences?tab=resume', icon: FileText },
  ];

  return (
    <>
      {/* Backdrop Overlay */}
      <div 
        className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-50 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />

      {/* Slide-out Sidebar Drawer */}
      <div 
        className={`fixed top-0 left-0 h-full w-[290px] sm:w-[320px] bg-[#FDFBF7] shadow-2xl flex flex-col z-50 border-r border-gray-200 transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Drawer Header */}
        <div className="p-5 flex items-center justify-between border-b border-gray-100 bg-white/60">
          <Link href="/" onClick={onClose} className="flex items-center gap-2.5 text-orange-600 group">
            <div className="w-9 h-9 rounded-xl bg-orange-100 flex items-center justify-center text-orange-600 group-hover:scale-105 transition-transform">
              <Compass className="h-6 w-6" />
            </div>
            <span className="font-extrabold text-xl tracking-tight text-gray-900">Career Maps</span>
          </Link>

          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition"
            title="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        
        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto py-4 px-3.5">
          <nav className="space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href.split('?')[0] || (pathname === '/' && item.href === '/');
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={`flex items-center justify-between px-3.5 py-3 text-sm font-semibold rounded-xl transition-all group ${
                    isActive 
                      ? 'bg-orange-600 text-white shadow-md shadow-orange-600/20' 
                      : 'text-gray-700 hover:bg-orange-50/70 hover:text-orange-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-5 w-5 shrink-0 ${isActive ? 'text-white' : 'text-gray-400 group-hover:text-orange-500 transition-colors'}`} />
                    <span>{item.name}</span>
                  </div>
                  <ChevronRight className={`h-4 w-4 ${isActive ? 'text-orange-200' : 'text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity'}`} />
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Info / Logout Footer */}
        <div className="p-4 border-t border-gray-100 bg-white/60">
          {isAuthenticated && user ? (
            <div className="flex items-center justify-between gap-3">
              <Link 
                href="/profile" 
                onClick={onClose}
                className="flex items-center gap-3 min-w-0 hover:opacity-80 transition"
              >
                {user.profile_image ? (
                  <img src={user.profile_image} alt="" className="h-9 w-9 rounded-full bg-gray-200 object-cover shrink-0" />
                ) : (
                  <div className="h-9 w-9 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center font-bold text-xs shrink-0">
                    {user.name?.charAt(0) || user.email?.charAt(0) || 'U'}
                  </div>
                )}
                <div className="truncate">
                  <div className="text-xs font-bold text-gray-900 truncate">{user.name || 'User'}</div>
                  <div className="text-[10px] text-gray-500 truncate">{user.email}</div>
                </div>
              </Link>
              <button 
                onClick={() => {
                  logout();
                  onClose();
                }}
                className="p-2 rounded-xl text-gray-400 hover:text-red-600 hover:bg-red-50 transition"
                title="Log Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link 
                href="/login" 
                onClick={onClose}
                className="flex-1 text-center py-2 px-3 rounded-xl border border-gray-200 text-xs font-bold text-gray-700 hover:bg-gray-50 transition"
              >
                Log In
              </Link>
              <Link 
                href="/register" 
                onClick={onClose}
                className="flex-1 text-center py-2 px-3 rounded-xl bg-orange-600 text-xs font-bold text-white hover:bg-orange-700 shadow-sm transition"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>

      </div>
    </>
  );
}
