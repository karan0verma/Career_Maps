import { Hero } from '../components/Hero';
import { JobsFeed } from '../components/JobsFeed';
import { fetchStats } from '../lib/api';

// Revalidate stats every minute
export const revalidate = 60;

export default async function Home() {
  let stats = { jobs: 0, companies: 0 };
  
  try {
    stats = await fetchStats();
  } catch (error) {
    console.error('Failed to load stats:', error);
  }

  return (
    <main className="min-h-screen bg-background">
      <Hero jobCount={stats.jobs} companyCount={stats.companies} />
      <JobsFeed />
    </main>
  );
}
