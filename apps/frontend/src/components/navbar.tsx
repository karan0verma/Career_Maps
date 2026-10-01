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
      <div className="container mx-auto flex flex-col lg:flex-row h-auto lg:h-20 py-2 lg:py-0 items-center justify-between px-2 lg:px-6 gap-2 lg:gap-0">
        
        {/* Top Row on mobile / Left side on desktop */}
        <div className="w-full lg:w-auto flex items-center justify-between lg:justify-start gap-2 lg:gap-4 shrink-0">
          <div className="flex items-center gap-2">
            {/* 3-Line Hamburger Menu Button */}
            <button
              onClick={onOpenMenu}
              className="p-1.5 lg:p-2 rounded-xl bg-orange-50 hover:bg-orange-100 text-orange-600 hover:text-orange-700 transition flex items-center justify-center group"
              title="Open Navigation"
            >
              <Menu className="h-5 w-5 transition-transform group-hover:scale-110" />
            </button>
  
            <Link href="/" className="flex items-center gap-2 text-orange-600">
              <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-xl bg-orange-100 flex items-center justify-center text-orange-600">
                <Compass className="h-4 w-4 lg:h-5 lg:w-5" />
              </div>
              <span className="inline-block font-extrabold text-lg lg:text-xl tracking-tight text-gray-900">Career Maps</span>
            </Link>
          </div>

          {/* Right items on mobile */}
          <div className="flex lg:hidden items-center gap-2 shrink-0">
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

        {/* Live Ticker: 2nd Row on mobile / Center on desktop */}
        <div className="w-full lg:flex-1 lg:px-4 order-last lg:order-none min-w-0 overflow-hidden mt-1 lg:mt-0">
          <HeaderLiveTicker />
        </div>

        {/* Right items on Desktop */}
        <div className="hidden lg:flex items-center gap-2 lg:gap-3 shrink-0">
          {isLoggedIn ? (
            <>
              <Link href="/profile/applied" className="text-sm font-medium text-gray-600 hover:text-orange-600 transition-colors">
                Applied Jobs
              </Link>
              <Link href="/profile/saved" className="text-sm font-medium text-gray-600 hover:text-orange-600 transition-colors">
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
              <Link href="/register" className="bg-orange-600 hover:bg-orange-700 text-white text-xs lg:text-sm font-bold px-4 py-2 rounded-xl shadow-xs transition">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
