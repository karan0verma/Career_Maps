import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { CrawlerResultDto, CrawlerHeartbeatDto } from '@career-maps/shared';

@Injectable()
export class CrawlerService {
  constructor(private readonly prisma: PrismaService) {}

  async getQueue(limit: number = 10, offset: number = 0) {
    const now = new Date();
    
    return this.prisma.company.findMany({
      where: {
        crawlerEnabled: true,
        OR: [
          { nextCrawlAt: { lte: now } },
          { nextCrawlAt: null }
        ]
      },
      take: limit,
      skip: offset,
      orderBy: {
        nextCrawlAt: 'asc'
      },
      select: {
        id: true,
        companyName: true,
        slug: true,
        officialCareerPage: true,
        crawlFrequencyHours: true,
        atsType: true,
        opportunities: {
          select: { id: true, slug: true }
        }
      }
    });
  }

  async processResult(result: CrawlerResultDto) {
    const company = await this.prisma.company.findUnique({
      where: { id: result.companyId }
    });

    if (!company) {
      throw new NotFoundException('Company not found');
    }

    const nextCrawlAt = new Date();
    nextCrawlAt.setHours(nextCrawlAt.getHours() + company.crawlFrequencyHours);

    // Use Prisma transaction for atomic updates
    return this.prisma.$transaction(async (tx) => {
      // 1. Mark missing opportunities as closed (inactive)
      if (result.inactiveOpportunities.length > 0) {
        await tx.opportunity.updateMany({
          where: {
            id: { in: result.inactiveOpportunities },
            companyId: company.id
          },
          data: { status: 'closed' }
        });
      }

      // 2. Insert new opportunities
      if (result.newOpportunities.length > 0) {
        const createData = result.newOpportunities.map(opp => ({
          companyId: company.id,
          title: opp.title,
          slug: opp.slug,
          category: opp.category,
          employmentType: opp.employmentType,
          location: opp.location,
          city: opp.city,
          state: opp.state,
          country: opp.country ?? null,
          isRemote: opp.isRemote ?? false,
          isHybrid: opp.isHybrid ?? false,
          salary: opp.salary,
          applyUrl: opp.applyUrl,
          officialSourceUrl: opp.officialSourceUrl,
          sourceATS: opp.sourceATS ?? null,
          externalJobId: opp.externalJobId ?? null,
          description: opp.description ?? null,
          publishedDate: new Date(),
          status: 'open'
        }));
        
        await tx.opportunity.createMany({
          data: createData
        });
      }

      // 3. Update existing opportunities (e.g., refresh updated_at, reset status to open)
      if (result.updatedOpportunities.length > 0) {
        await tx.opportunity.updateMany({
          where: {
            id: { in: result.updatedOpportunities },
            companyId: company.id
          },
          data: {
            status: 'open',
            updatedAt: new Date()
          }
        });
      }

      // 4. Update the company metrics and crawler state
      return tx.company.update({
        where: { id: company.id },
        data: {
          lastCrawledAt: new Date(),
          nextCrawlAt,
          crawlerStatus: result.status === 'success' ? 'idle' : 'error',
          totalLiveJobs: result.totalLiveJobs
        }
      });
    });
  }

  async registerHeartbeat(data: CrawlerHeartbeatDto) {
    // In a real application, this might store the heartbeat in Redis or a dedicated telemetry table.
    // For now, we will just return success so the Admin Dashboard knows the endpoint is alive.
    return {
      status: data.status,
      lastSeen: new Date(),
      uptime: data.uptime,
      error: data.lastError
    };
  }
}
