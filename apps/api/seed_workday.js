const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const companies = [
    {
      companyName: 'NVIDIA',
      slug: 'nvidia',
      officialCareerPage: 'https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite',
      atsType: 'WORKDAY',
      atsVerified: true,
      crawlerEnabled: true,
      nextCrawlAt: new Date()
    },
    {
      companyName: 'Electronic Arts',
      slug: 'electronic-arts',
      officialCareerPage: 'https://ea.wd5.myworkdayjobs.com/ext',
      atsType: 'WORKDAY',
      atsVerified: true,
      crawlerEnabled: true,
      nextCrawlAt: new Date()
    },
    {
      companyName: 'Broken Workday Co',
      slug: 'broken-workday-co',
      officialCareerPage: 'https://invalid.wd5.not-myworkday.com/jobs',
      atsType: 'WORKDAY',
      atsVerified: true,
      crawlerEnabled: true,
      nextCrawlAt: new Date()
    }
  ];

  for (const c of companies) {
    await prisma.company.upsert({
      where: { slug: c.slug },
      update: {
        atsType: c.atsType,
        atsVerified: c.atsVerified,
        crawlerEnabled: c.crawlerEnabled,
        nextCrawlAt: c.nextCrawlAt,
        officialCareerPage: c.officialCareerPage
      },
      create: c
    });
    console.log(`Upserted ${c.companyName}`);
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
