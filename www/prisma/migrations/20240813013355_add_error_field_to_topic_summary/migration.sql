/*
  Warnings:

  - You are about to drop the column `lastGeneratedAt` on the `TopicSummary` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "TopicSummary" DROP COLUMN "lastGeneratedAt",
ADD COLUMN     "error" BOOLEAN NOT NULL DEFAULT false;
