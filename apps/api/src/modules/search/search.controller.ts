import { Controller, Get, Query } from '@nestjs/common';
import { SearchService } from './search.service';

@Controller('search')
export class SearchController {
  constructor(private readonly searchService: SearchService) {}

  @Get()
  async searchOpportunities(
    @Query('q') query: string = '',
    @Query('page') page: string = '1',
    @Query('limit') limit: string = '20'
  ) {
    return {
      success: true,
      message: 'Search completed',
      data: await this.searchService.search(query, parseInt(page, 10), parseInt(limit, 10)),
      timestamp: new Date().toISOString()
    };
  }
}
