import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class OpportunitiesService {
  constructor(private readonly prisma: PrismaService) {}

  async findLatest(page: number, limit: number) {
    const skip = (page - 1) * limit;
    return this.prisma.opportunity.findMany({
      skip,
      take: limit,
      where: { status: 'open' },
      orderBy: { publishedDate: 'desc' },
      include: {
        company: {
          select: { companyName: true, logoUrl: true, slug: true }
        }
      }
    });
  }

  async findBySlug(slug: string) {
    const opp = await this.prisma.opportunity.findUnique({
      where: { slug },
      include: {
        company: true,
        skills: { include: { skill: true } }
      }
    });
    
    if (!opp) {
      throw new NotFoundException('Opportunity not found');
    }
    
    return opp;
  }
}
