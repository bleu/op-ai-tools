/*
  Warnings:

  - You are about to drop the column `needsSummarize` on the `RawTopic` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "RawTopic" DROP COLUMN "needsSummarize",
ADD COLUMN     "lastSummarizedAt" TIMESTAMP(3);
