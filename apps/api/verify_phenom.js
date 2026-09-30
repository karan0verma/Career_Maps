const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const opps = await prisma.opportunity.findMany({
    where: { sourceATS: 'PHENOM' }
  });
  console.log(`Found ${opps.length} Phenom opportunities in database.`);
  if (opps.length > 0) {
      console.log(opps[0]);
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
