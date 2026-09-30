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
      <div className="container mx-auto flex flex-col sm:flex-row h-auto sm:h-20 py-2 sm:py-0 items-center justify-between px-2 sm:px-6 gap-2 sm:gap-0">
        
        <div className="w-full sm:w-auto flex items-center justify-between sm:justify-start gap-2 sm:gap-4 shrink-0">
          <div className="flex items-center gap-2">
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

          {/* Right items on mobile */}
          <div className="flex sm:hidden items-center gap-2 shrink-0">
            {isLoggedIn ? (
              <>
                <Link href="/profile" className={buttonVariants({ variant: "outline", size: "sm" })}>
                  Profile
                </Link>
                <Button variant="ghost" size="sm" onClick={logout} className="px-2">
                  Log Out
                </Button>
              </>
            ) : (
              <>
                <Link href="/login" className={buttonVariants({ variant: "ghost", size: "sm" })}>
                  Log In
                </Link>
                <Link href="/register" className="bg-orange-600 hover:bg-orange-700 text-white text-[11px] font-bold px-3 py-1.5 rounded-xl shadow-xs transition">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Live Ticker in Navbar (Full width on mobile) */}
        <div className="w-full sm:flex-1 sm:px-4 order-last sm:order-none min-w-0 overflow-hidden mt-1 sm:mt-0">
          <HeaderLiveTicker />
        </div>

        {/* Right items on Desktop */}
        <div className="hidden sm:flex items-center gap-2 md:gap-3 shrink-0">
          {isLoggedIn ? (
            <>
              <Link href="/profile/saved" className="text-sm font-medium text-gray-600 hover:text-orange-600 transition-colors hidden md:block">
                Saved Jobs
              </Link>
              <Link href="/profile" className={buttonVariants({ variant: "outline", size: "sm" })}>
                Profile
              </Link>
              <Button variant="ghost" size="sm" onClick={logout}>
                Log Out
              </Button>
            </>
          ) : (
            <>
              <Link href="/login" className={buttonVariants({ variant: "ghost", size: "sm" })}>
                Log In
              </Link>
              <Link href="/register" className="bg-orange-600 hover:bg-orange-700 text-white text-xs sm:text-sm font-bold px-4 py-2 rounded-xl shadow-xs transition">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
