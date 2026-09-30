import { Controller, Post, Body, Headers, UnauthorizedException } from '@nestjs/common';
import { AuthService } from './auth.service';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('webhook')
  async clerkWebhook(@Body() payload: any, @Headers('svix-signature') signature: string) {
    if (!signature) {
      throw new UnauthorizedException('Missing signature');
    }
    // Note: Verify svix signature using CLERK_WEBHOOK_SECRET in production
    return this.authService.syncUser(payload);
  }
}
