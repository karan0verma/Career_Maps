import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { UsersService } from '../users/users.service';

@Injectable()
export class RecommendationsService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly usersService: UsersService
  ) {}

  async generateForUser(userId: string) {
    const profile = await this.usersService.findProfileByUserId(userId);
    
    // Extract preferences
    const preferredRoles = profile.preferredRoles.map((r: any) => r.roleName);
    const preferredLocations = profile.preferredLocations.map((l: any) => l.locationName);

    // Dynamic filtering based on preferences
    const recommended = await this.prisma.opportunity.findMany({
      where: {
        status: 'open',
        OR: [
          { category: { in: preferredRoles } },
          { city: { in: preferredLocations } }
        ]
      },
      take: 20,
      orderBy: { publishedDate: 'desc' },
      include: {
        company: { select: { companyName: true, logoUrl: true } }
      }
    });

    return recommended;
  }
}
