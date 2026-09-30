import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { CreateCompanyDto, UpdateCompanyDto, CrawlerConfigDto } from '@career-maps/shared';

@Injectable()
export class AdminService {
  constructor(private readonly prisma: PrismaService) {}

  async getStats() {
    const totalUsers = await this.prisma.user.count();
    const activeOpportunities = await this.prisma.opportunity.count({ where: { status: 'open' } });
    const totalCompanies = await this.prisma.company.count();
    
    return {
      totalUsers,
      activeOpportunities,
      totalCompanies,
      crawlerHealth: "Operational"
    };
  }

  async addCompany(data: CreateCompanyDto) {
    return this.prisma.company.create({
      data: {
        companyName: data.companyName,
        slug: data.slug,
        logoUrl: data.logoUrl,
        website: data.website,
        officialCareerPage: data.officialCareerPage,
        companyType: data.companyType,
        industry: data.industry,
        country: data.country,
        state: data.state,
        city: data.city,
        headquarters: data.headquarters,
        description: data.description,
        careersSupported: data.careersSupported,
        linkedInUrl: data.linkedInUrl,
        foundedYear: data.foundedYear,
      }
    });
  }

  async updateCompany(id: string, data: UpdateCompanyDto) {
    const exists = await this.prisma.company.findUnique({ where: { id } });
    if (!exists) throw new NotFoundException('Company not found');
    
    return this.prisma.company.update({
      where: { id },
      data,
    });
  }

  async updateCrawlerConfig(id: string, config: CrawlerConfigDto) {
    const exists = await this.prisma.company.findUnique({ where: { id } });
    if (!exists) throw new NotFoundException('Company not found');

    // If crawler is being newly enabled, set nextCrawlAt to now
    let nextCrawlAt = exists.nextCrawlAt;
    if (config.crawlerEnabled && !exists.crawlerEnabled) {
      nextCrawlAt = new Date();
    } else if (!config.crawlerEnabled) {
      nextCrawlAt = null; // Disable future crawls
    }

    return this.prisma.company.update({
      where: { id },
      data: {
        crawlerEnabled: config.crawlerEnabled,
        crawlFrequencyHours: config.crawlFrequencyHours,
        nextCrawlAt,
      }
    });
  }
}
