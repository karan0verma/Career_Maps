const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const opps = await prisma.opportunity.findMany({
    where: { company: { companyName: 'Mastercard' } }
  });
  console.log(`Found ${opps.length} opportunities for Mastercard.`);
  if (opps.length > 0) {
    console.log(opps[0]);
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
