import { Controller, Get, Param, Query } from '@nestjs/common';
import { CompaniesService } from './companies.service';

@Controller('companies')
export class CompaniesController {
  constructor(private readonly companiesService: CompaniesService) {}

  @Get()
  async listCompanies(
    @Query('page') page: string = '1', 
    @Query('limit') limit: string = '20'
  ) {
    const pageNumber = parseInt(page, 10);
    const limitNumber = parseInt(limit, 10);
    
    return {
      success: true,
      message: 'Companies retrieved successfully',
      data: await this.companiesService.findAll(pageNumber, limitNumber),
      timestamp: new Date().toISOString()
    };
  }

  @Get(':slug')
  async getCompanyBySlug(@Param('slug') slug: string) {
    return {
      success: true,
      message: 'Company retrieved successfully',
      data: await this.companiesService.findBySlug(slug),
      timestamp: new Date().toISOString()
    };
  }
}
