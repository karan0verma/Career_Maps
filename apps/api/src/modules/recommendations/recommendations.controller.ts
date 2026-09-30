import { Controller, Get, Param } from '@nestjs/common';
import { RecommendationsService } from './recommendations.service';

@Controller('recommendations')
export class RecommendationsController {
  constructor(private readonly recommendationsService: RecommendationsService) {}

  @Get('user/:userId')
  async getRecommendations(@Param('userId') userId: string) {
    return {
      success: true,
      message: 'Personalized recommendations generated',
      data: await this.recommendationsService.generateForUser(userId),
      timestamp: new Date().toISOString()
    };
  }
}
