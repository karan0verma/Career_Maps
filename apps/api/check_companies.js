const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const companies = await prisma.company.findMany();
  for (let c of companies) {
      console.log(`${c.companyName} | ${c.slug} | ${c.atsType}`);
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
