/*
  Warnings:

  - You are about to drop the column `careersUrl` on the `Company` table. All the data in the column will be lost.
  - You are about to drop the column `logo` on the `Company` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `Company` table. All the data in the column will be lost.
  - Added the required column `companyName` to the `Company` table without a default value. This is not possible if the table is not empty.
  - Added the required column `officialCareerPage` to the `Company` table without a default value. This is not possible if the table is not empty.

*/
-- RedefineTables
PRAGMA defer_foreign_keys=ON;
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Company" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "companyName" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "logoUrl" TEXT,
    "website" TEXT,
    "officialCareerPage" TEXT NOT NULL,
    "companyType" TEXT,
    "industry" TEXT,
    "country" TEXT NOT NULL DEFAULT 'India',
    "state" TEXT,
    "city" TEXT,
    "headquarters" TEXT,
    "description" TEXT,
    "careersSupported" BOOLEAN NOT NULL DEFAULT true,
    "crawlerEnabled" BOOLEAN NOT NULL DEFAULT false,
    "crawlFrequencyHours" INTEGER NOT NULL DEFAULT 24,
    "lastCrawledAt" DATETIME,
    "nextCrawlAt" DATETIME,
    "crawlerStatus" TEXT NOT NULL DEFAULT 'idle',
    "totalLiveJobs" INTEGER NOT NULL DEFAULT 0,
    "status" TEXT NOT NULL DEFAULT 'active',
    "linkedInUrl" TEXT,
    "foundedYear" INTEGER,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL,
    "deletedAt" DATETIME
);
INSERT INTO "new_Company" ("companyType", "createdAt", "deletedAt", "description", "foundedYear", "headquarters", "id", "industry", "linkedInUrl", "slug", "status", "updatedAt", "website") SELECT "companyType", "createdAt", "deletedAt", "description", "foundedYear", "headquarters", "id", "industry", "linkedInUrl", "slug", "status", "updatedAt", "website" FROM "Company";
DROP TABLE "Company";
ALTER TABLE "new_Company" RENAME TO "Company";
CREATE UNIQUE INDEX "Company_companyName_key" ON "Company"("companyName");
CREATE UNIQUE INDEX "Company_slug_key" ON "Company"("slug");
CREATE INDEX "Company_companyName_idx" ON "Company"("companyName");
CREATE INDEX "Company_crawlerEnabled_idx" ON "Company"("crawlerEnabled");
CREATE INDEX "Company_nextCrawlAt_idx" ON "Company"("nextCrawlAt");
CREATE INDEX "Company_companyType_idx" ON "Company"("companyType");
PRAGMA foreign_keys=ON;
PRAGMA defer_foreign_keys=OFF;
