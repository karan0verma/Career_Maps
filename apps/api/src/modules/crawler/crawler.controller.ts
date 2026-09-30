import { Controller, Get, Post, Body, Query, BadRequestException } from '@nestjs/common';
import { CrawlerService } from './crawler.service';
import { CrawlerResultSchema, CrawlerHeartbeatSchema } from '@career-maps/shared';

@Controller('crawler')
export class CrawlerController {
  constructor(private readonly crawlerService: CrawlerService) {}

  @Get('queue')
  async getQueue(
    @Query('limit') limit: string = '10',
    @Query('offset') offset: string = '0'
  ) {
    const l = parseInt(limit, 10);
    const o = parseInt(offset, 10);
    
    if (isNaN(l) || isNaN(o)) {
      throw new BadRequestException('Invalid pagination parameters');
    }

    return {
      success: true,
      data: await this.crawlerService.getQueue(l, o)
    };
  }

  @Post('result')
  async processResult(@Body() body: any) {
    const parsed = CrawlerResultSchema.safeParse(body);
    
    if (!parsed.success) {
      throw new BadRequestException(parsed.error.format());
    }

    return {
      success: true,
      data: await this.crawlerService.processResult(parsed.data)
    };
  }

  @Post('heartbeat')
  async registerHeartbeat(@Body() body: any) {
    const parsed = CrawlerHeartbeatSchema.safeParse(body);

    if (!parsed.success) {
      throw new BadRequestException(parsed.error.format());
    }

    return {
      success: true,
      data: await this.crawlerService.registerHeartbeat(parsed.data)
    };
  }
}
