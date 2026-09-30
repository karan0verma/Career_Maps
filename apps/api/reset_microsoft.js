const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  await prisma.company.updateMany({
    where: { slug: 'microsoft' },
    data: { nextCrawlAt: new Date(Date.now() - 3600000) } // 1 hour ago
  });
  console.log('Reset Microsoft nextCrawlAt');
}

main().catch(console.error).finally(() => prisma.$disconnect());
