const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  await prisma.company.create({
    data: {
      companyName: 'Mastercard',
      slug: 'mastercard',
      officialCareerPage: 'https://mastercard.wd1.myworkdayjobs.com/CorporateCareers',
      atsType: 'WORKDAY',
      crawlerEnabled: true,
      nextCrawlAt: new Date()
    }
  });
  console.log('Inserted Mastercard with ATS Type WORKDAY.');
  
  const meta = await prisma.company.findFirst({ where: { companyName: 'Meta' } });
  if (meta) {
    await prisma.company.update({
      where: { id: meta.id },
      data: { atsType: 'UNKNOWN', crawlerEnabled: false }
    });
    console.log('Reverted Meta to UNKNOWN and disabled crawler.');
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
