const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  await prisma.company.updateMany({
    where: { slug: 'nvidia' },
    data: { nextCrawlAt: new Date(Date.now() - 1000 * 60 * 60) } // 1 hour ago
  });
  console.log('Reset NVIDIA nextCrawlAt');
}

main().catch(console.error).finally(() => prisma.$disconnect());
