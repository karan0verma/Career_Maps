const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  await prisma.company.updateMany({
    where: { slug: 'microsoft' },
    data: { atsType: 'PHENOM', atsVerified: true, crawlerEnabled: true, nextCrawlAt: new Date(Date.now() - 3600000) }
  });
  
  await prisma.company.updateMany({
    where: { slug: 'wipro' },
    data: { atsType: 'SUCCESSFACTORS_RMK', atsVerified: true }
  });

  console.log('Updated Microsoft and Wipro ATS types');
}

main().catch(console.error).finally(() => prisma.$disconnect());
