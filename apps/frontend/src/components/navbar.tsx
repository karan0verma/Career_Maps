"use client";

import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Compass, Menu } from "lucide-react";
import { HeaderLiveTicker } from "./HeaderLiveTicker";

interface NavbarProps {
  onOpenMenu?: () => void;
}

export function Navbar({ onOpenMenu }: NavbarProps) {
  const { isLoggedIn, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white/85 backdrop-blur-md shadow-xs">
      <div className="container mx-auto flex flex-col py-2 sm:py-3 px-2 sm:px-6 gap-2">
        
        {/* Top Row: Logo & Buttons */}
        <div className="w-full flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2 sm:gap-4">
            {/* 3-Line Hamburger Menu Button */}
            <button
              onClick={onOpenMenu}
              className="p-1.5 sm:p-2 rounded-xl bg-orange-50 hover:bg-orange-100 text-orange-600 hover:text-orange-700 transition flex items-center justify-center group"
              title="Open Navigation"
            >
              <Menu className="h-5 w-5 transition-transform group-hover:scale-110" />
            </button>
  
            <Link href="/" className="flex items-center gap-2 text-orange-600">
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-orange-100 flex items-center justify-center text-orange-600">
                <Compass className="h-4 w-4 sm:h-5 sm:w-5" />
              </div>
              <span className="inline-block font-extrabold text-lg sm:text-xl tracking-tight text-gray-900 hidden sm:inline-block">Career Maps</span>
            </Link>
          </div>

          {/* Right items */}
          <div className="flex items-center gap-2 shrink-0">
            {isLoggedIn ? (
              <>
                <Link href="/profile/saved" className="hidden sm:block text-sm font-medium text-gray-600 hover:text-orange-600 transition-colors">
                  Saved Jobs
                </Link>
                <Link href="/profile" className={buttonVariants({ variant: "outline", size: "sm" })}>
                  Profile
                </Link>
                <Button variant="ghost" size="sm" onClick={logout} className="px-2 sm:px-4">
                  Log Out
                </Button>
              </>
            ) : (
              <>
                <Link href="/login" className={buttonVariants({ variant: "ghost", size: "sm" })}>
                  Log In
                </Link>
                <Link href="/register" className="bg-orange-600 hover:bg-orange-700 text-white text-[11px] sm:text-sm font-bold px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl shadow-xs transition">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Bottom Row: Live Ticker (Full width on all devices) */}
        <div className="w-full min-w-0 overflow-hidden">
          <HeaderLiveTicker />
        </div>
      </div>
    </header>
  );
}
