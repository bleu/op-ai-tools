/*
  Warnings:

  - You are about to drop the `RawTopicSummary` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "RawTopicSummary";

-- CreateTable
CREATE TABLE "TopicSummary" (
    "id" SERIAL NOT NULL,
    "url" TEXT NOT NULL,
    "data" JSONB NOT NULL,
    "lastGeneratedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "TopicSummary_pkey" PRIMARY KEY ("id")
);
