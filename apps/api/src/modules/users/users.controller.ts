import { Controller, Get, Param } from '@nestjs/common';
import { UsersService } from './users.service';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get(':id')
  async getUser(@Param('id') id: string) {
    return {
      success: true,
      message: 'User retrieved successfully',
      data: await this.usersService.findById(id),
      timestamp: new Date().toISOString()
    };
  }

  @Get(':id/profile')
  async getUserProfile(@Param('id') id: string) {
    return {
      success: true,
      message: 'User profile retrieved successfully',
      data: await this.usersService.findProfileByUserId(id),
      timestamp: new Date().toISOString()
    };
  }
}
