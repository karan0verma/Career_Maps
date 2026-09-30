import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class AuthService {
  constructor(private readonly prisma: PrismaService) {}

  async syncUser(payload: any) {
    const { type, data } = payload;
    
    if (type === 'user.created' || type === 'user.updated') {
      const email = data.email_addresses?.[0]?.email_address || '';
      const fullName = `${data.first_name || ''} ${data.last_name || ''}`.trim() || 'Unknown';
      
      // @ts-ignore
      await this.prisma.user.upsert({
        where: { id: data.id },
        update: {
          email,
          fullName,
          profileImage: data.image_url,
        },
        create: {
          id: data.id,
          email,
          fullName,
          profileImage: data.image_url,
        }
      });
    }

    if (type === 'user.deleted') {
      // @ts-ignore
      await this.prisma.user.update({
        where: { id: data.id },
        data: { accountStatus: 'deleted', deletedAt: new Date() }
      });
    }

    return { success: true };
  }
}
