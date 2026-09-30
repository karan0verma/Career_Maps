import { z } from 'zod';

export const CreateCompanySchema = z.object({
  companyName: z.string().min(2, "Company name must be at least 2 characters"),
  slug: z.string().min(2, "Slug must be at least 2 characters"),
  logoUrl: z.string().url("Must be a valid URL").optional().or(z.literal('')),
  website: z.string().url("Must be a valid URL").optional().or(z.literal('')),
  officialCareerPage: z.string().url("Must be a valid URL"),
  companyType: z.string().optional(),
  industry: z.string().optional(),
  country: z.string().default('India'),
  state: z.string().optional(),
  city: z.string().optional(),
  headquarters: z.string().optional(),
  description: z.string().optional(),
  careersSupported: z.boolean().default(true),
  linkedInUrl: z.string().url("Must be a valid URL").optional().or(z.literal('')),
  foundedYear: z.number().int().positive().optional(),
});

export const UpdateCompanySchema = CreateCompanySchema.partial();

export const CrawlerConfigSchema = z.object({
  crawlerEnabled: z.boolean(),
  crawlFrequencyHours: z.number().int().positive().min(1).max(720),
});

export type CreateCompanyDto = z.infer<typeof CreateCompanySchema>;
export type UpdateCompanyDto = z.infer<typeof UpdateCompanySchema>;
export type CrawlerConfigDto = z.infer<typeof CrawlerConfigSchema>;
