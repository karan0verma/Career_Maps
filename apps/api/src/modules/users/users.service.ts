import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

  async findById(id: string) {
    const user = await this.prisma.user.findUnique({
      where: { id },
    });
    if (!user) {
      throw new NotFoundException('User not found');
    }
    return user;
  }

  async findProfileByUserId(userId: string) {
    const profile = await this.prisma.userProfile.findUnique({
      where: { userId },
      include: {
        skills: { include: { skill: true } },
        preferredRoles: true,
        preferredLocations: true,
        preferredIndustries: true,
      }
    });
    if (!profile) {
      throw new NotFoundException('User profile not found');
    }
    return profile;
  }
}
