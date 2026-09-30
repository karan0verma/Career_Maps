import { Controller, Get, Post, Patch, Param, Body, BadRequestException } from '@nestjs/common';
import { AdminService } from './admin.service';
import { CreateCompanySchema, UpdateCompanySchema, CrawlerConfigSchema } from '@career-maps/shared';

@Controller('admin')
export class AdminController {
  constructor(private readonly adminService: AdminService) {}

  @Get('dashboard')
  async getDashboardStats() {
    return {
      success: true,
      data: await this.adminService.getStats(),
      timestamp: new Date().toISOString()
    };
  }

  @Post('companies')
  async addCompany(@Body() body: any) {
    const parsed = CreateCompanySchema.safeParse(body);
    if (!parsed.success) {
      throw new BadRequestException(parsed.error.format());
    }
    
    return {
      success: true,
      data: await this.adminService.addCompany(parsed.data),
    };
  }

  @Patch('companies/:id')
  async updateCompany(@Param('id') id: string, @Body() body: any) {
    const parsed = UpdateCompanySchema.safeParse(body);
    if (!parsed.success) {
      throw new BadRequestException(parsed.error.format());
    }

    return {
      success: true,
      data: await this.adminService.updateCompany(id, parsed.data),
    };
  }

  @Patch('companies/:id/crawler')
  async updateCrawlerConfig(@Param('id') id: string, @Body() body: any) {
    const parsed = CrawlerConfigSchema.safeParse(body);
    if (!parsed.success) {
      throw new BadRequestException(parsed.error.format());
    }

    return {
      success: true,
      data: await this.adminService.updateCrawlerConfig(id, parsed.data),
    };
  }
}
