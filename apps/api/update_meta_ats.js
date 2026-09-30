const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const meta = await prisma.company.findFirst({
    where: { companyName: 'Meta' }
  });
  
  if (meta) {
    await prisma.company.update({
      where: { id: meta.id },
      data: { atsType: 'WORKDAY', crawlerEnabled: true, nextCrawlAt: new Date() }
    });
    console.log(`Updated Meta with ATS Type WORKDAY. (ID: ${meta.id})`);
  } else {
    console.log('Meta not found in database.');
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
