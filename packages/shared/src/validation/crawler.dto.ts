import { z } from 'zod';

export const CrawlerResultSchema = z.object({
  companyId: z.string().uuid(),
  status: z.enum(['success', 'failed']),
  totalLiveJobs: z.number().int().nonnegative(),
  newOpportunities: z.array(z.object({
    title: z.string(),
    slug: z.string(),
    category: z.string(),
    employmentType: z.string(),
    location: z.string().nullish(),
    city: z.string().nullish(),
    state: z.string().nullish(),
    country: z.string().nullish(),
    isRemote: z.boolean().default(false),
    isHybrid: z.boolean().default(false),
    salary: z.string().nullish(),
    applyUrl: z.string().url(),
    officialSourceUrl: z.string().url(),
    sourceATS: z.string().nullish(),
    externalJobId: z.string().nullish(),
    description: z.string().nullish(),
  })),
  updatedOpportunities: z.array(z.string().uuid()),
  inactiveOpportunities: z.array(z.string().uuid()),
});

export const CrawlerHeartbeatSchema = z.object({
  status: z.enum(['running', 'idle', 'error']),
  uptime: z.number(),
  lastError: z.string().optional(),
});

export type CrawlerResultDto = z.infer<typeof CrawlerResultSchema>;
export type CrawlerHeartbeatDto = z.infer<typeof CrawlerHeartbeatSchema>;
