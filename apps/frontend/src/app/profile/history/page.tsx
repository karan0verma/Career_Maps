"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiRequest } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";

interface SearchHistory {
  id: string;
  query: string;
  location: string;
  work_mode: string;
  searched_at: string;
}

export default function SearchHistoryPage() {
  const router = useRouter();
  const [history, setHistory] = useState<SearchHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true);
      try {
        const data = await apiRequest("/users/me/history");
        setHistory(data || []);
      } catch (err) {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };
    
    if (!localStorage.getItem("access_token")) {
      router.push("/login");
    } else {
      loadHistory();
    }
  }, [router]);

  if (loading) {
    return <div className="animate-pulse h-64 bg-gray-100 rounded-xl"></div>;
  }

  return (
    <Card className="shadow-sm border-gray-200 min-h-[400px]">
      <CardHeader className="border-b bg-gray-50/50">
        <div className="flex justify-between items-center">
          <CardTitle className="text-2xl">Search History</CardTitle>
          <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
            {history.length} Searches
          </span>
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        {history.length === 0 ? (
          <div className="text-center py-16">
            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            <h3 className="text-lg font-medium text-gray-900">No search history</h3>
            <p className="text-gray-500 mt-1 mb-6">You haven't made any searches yet.</p>
            <Link href="/jobs" className={buttonVariants({ variant: "default" })}>
              Search Jobs
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <div key={item.id} className="flex flex-col md:flex-row justify-between items-start md:items-center p-4 border border-gray-100 rounded-lg hover:border-gray-300 transition-colors">
                <div>
                  <h4 className="font-bold text-lg text-gray-900">
                    {item.query || "All Jobs"}
                  </h4>
                  <div className="text-gray-500 text-sm mt-1 flex space-x-3">
                    {item.location && <span>📍 {item.location}</span>}
                    {item.work_mode && <span>🏢 {item.work_mode}</span>}
                  </div>
                  <p className="text-xs text-gray-400 mt-2">Searched on {new Date(item.searched_at).toLocaleString()}</p>
                </div>
                <div className="mt-4 md:mt-0 flex space-x-2 w-full md:w-auto">
                  <Link href={`/jobs?q=${encodeURIComponent(item.query || "")}&location=${encodeURIComponent(item.location || "")}&work_mode=${encodeURIComponent(item.work_mode || "")}`} className={buttonVariants({ variant: "outline", size: "sm", className: "flex-1 md:flex-none" })}>
                    Run Search Again
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
