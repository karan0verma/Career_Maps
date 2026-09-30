import { Module } from '@nestjs/common';
import { PrismaModule } from './prisma/prisma.module';
import { UsersModule } from './modules/users/users.module';
import { CompaniesModule } from './modules/companies/companies.module';
import { OpportunitiesModule } from './modules/opportunities/opportunities.module';
import { AuthModule } from './modules/auth/auth.module';
import { SearchModule } from './modules/search/search.module';
import { RecommendationsModule } from './modules/recommendations/recommendations.module';
import { AdminModule } from './modules/admin/admin.module';
import { CrawlerModule } from './modules/crawler/crawler.module';

@Module({
  imports: [
    PrismaModule,
    AuthModule,
    UsersModule,
    CompaniesModule,
    OpportunitiesModule,
    SearchModule,
    RecommendationsModule,
    AdminModule,
    CrawlerModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
