import { JobsFeed } from "@/components/JobsFeed";

export const metadata = {
  title: 'Jobs - Career Maps',
  description: 'Find your next role',
};

export default function JobsPage() {
  return (
    <div className="bg-gray-50 min-h-screen">
      <JobsFeed />
    </div>
  );
}
