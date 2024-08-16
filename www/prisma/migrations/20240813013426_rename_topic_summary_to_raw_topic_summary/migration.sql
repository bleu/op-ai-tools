/*
  Warnings:

  - You are about to drop the `TopicSummary` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "TopicSummary";

-- CreateTable
CREATE TABLE "RawTopicSummary" (
    "id" SERIAL NOT NULL,
    "url" TEXT NOT NULL,
    "data" JSONB NOT NULL,
    "error" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "RawTopicSummary_pkey" PRIMARY KEY ("id")
);
