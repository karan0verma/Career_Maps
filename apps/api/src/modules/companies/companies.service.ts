import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class CompaniesService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(page: number, limit: number) {
    const skip = (page - 1) * limit;
    const companies = await this.prisma.company.findMany({
      skip,
      take: limit,
      where: { status: 'active' },
      orderBy: { companyName: 'asc' }
    });
    return companies;
  }

  async findBySlug(slug: string) {
    const company = await this.prisma.company.findUnique({
      where: { slug },
      include: {
        locations: true,
        opportunities: {
          where: { status: 'open' }
        }
      }
    });
    
    if (!company) {
      throw new NotFoundException('Company not found');
    }
    
    return company;
  }
}
