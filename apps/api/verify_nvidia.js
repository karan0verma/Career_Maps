const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const opps = await prisma.opportunity.findMany({
    where: { company: { companyName: 'NVIDIA' } },
    select: {
      id: true,
      title: true,
      slug: true,
      sourceATS: true,
      externalJobId: true,
      status: true
    }
  });
  console.log(`Found ${opps.length} opportunities for NVIDIA.`);
  if (opps.length > 0) {
    console.log(opps[0]);
  }
}

main().catch(console.error).finally(() => prisma.$disconnect());
