const { PrismaClient } = require('@prisma/client');
const { execSync } = require('child_process');
const fs = require('fs');

const prisma = new PrismaClient();

async function runCrawler() {
  const c = await prisma.company.findFirst({ where: { slug: 'google' } });
  await prisma.company.update({
    where: { id: c.id },
    data: { nextCrawlAt: new Date(Date.now() - 100000) }
  });
  
  try {
    execSync('.\\\\.venv312\\\\Scripts\\\\python.exe src\\\\main.py', {
      cwd: '../crawler',
      stdio: 'inherit',
      env: { ...process.env, PYTHONPATH: '.' }
    });
  } catch (e) {
    console.error("Crawler failed");
  }
}

async function getStats(cId) {
  const c = await prisma.company.findUnique({ where: { id: cId } });
  const openCount = await prisma.opportunity.count({ where: { companyId: cId, status: 'open' } });
  const closedCount = await prisma.opportunity.count({ where: { companyId: cId, status: 'closed' } });
  const totalDbCount = await prisma.opportunity.count({ where: { companyId: cId } });
  
  return {
    lastCrawledAt: c.lastCrawledAt,
    nextCrawlAt: c.nextCrawlAt,
    totalLiveJobs: c.totalLiveJobs,
    crawlerStatus: c.crawlerStatus,
    openCount,
    closedCount,
    totalDbCount
  };
}

async function main() {
  const c = await prisma.company.findFirst({ where: { slug: 'google' } });
  const cId = c.id;
  
  console.log("=== STARTING REGRESSION TEST ===");
  
  console.log("\\n--- RUN 1 (Normal) ---");
  await runCrawler();
  const stats1 = await getStats(cId);
  console.log("Stats after Run 1:");
  console.log(stats1);
  
  console.log("\\n--- RUN 2 (Simulating 5 missing jobs) ---");
  const crawlerPath = '../crawler/src/base_crawler.py';
  let originalCode = fs.readFileSync(crawlerPath, 'utf-8');
  let patchedCode = originalCode.replace(
    'def submit(self, scraped_jobs: list) -> Dict[str, Any]:',
    'def submit(self, scraped_jobs: list) -> Dict[str, Any]:\\n        scraped_jobs = scraped_jobs[:15]'
  );
  fs.writeFileSync(crawlerPath, patchedCode);
  
  await runCrawler();
  const stats2 = await getStats(cId);
  console.log("Stats after Run 2:");
  console.log(stats2);
  
  console.log("\\n--- RUN 3 (Restoring all jobs) ---");
  fs.writeFileSync(crawlerPath, originalCode);
  
  await runCrawler();
  const stats3 = await getStats(cId);
  console.log("Stats after Run 3:");
  console.log(stats3);
  
  console.log("\\n=== REGRESSION TEST COMPLETE ===");
}

main().then(() => prisma.$disconnect()).catch(console.error);
