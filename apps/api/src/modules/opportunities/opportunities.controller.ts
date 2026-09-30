import { Controller, Get, Param, Query } from '@nestjs/common';
import { OpportunitiesService } from './opportunities.service';

@Controller('opportunities')
export class OpportunitiesController {
  constructor(private readonly opportunitiesService: OpportunitiesService) {}

  @Get()
  async getLatestOpportunities(
    @Query('page') page: string = '1', 
    @Query('limit') limit: string = '20'
  ) {
    return {
      success: true,
      message: 'Latest opportunities retrieved successfully',
      data: await this.opportunitiesService.findLatest(parseInt(page, 10), parseInt(limit, 10)),
      timestamp: new Date().toISOString()
    };
  }

  @Get(':slug')
  async getOpportunityBySlug(@Param('slug') slug: string) {
    return {
      success: true,
      message: 'Opportunity retrieved successfully',
      data: await this.opportunitiesService.findBySlug(slug),
      timestamp: new Date().toISOString()
    };
  }
}
