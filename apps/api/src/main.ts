import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.setGlobalPrefix(`/api/v1`);
  app.enableCors();
  await app.listen(process.env.PORT || 4000);
  console.log(`Backend is running on http://localhost:${process.env.PORT || 4000}/api/v1`);
}
bootstrap();
