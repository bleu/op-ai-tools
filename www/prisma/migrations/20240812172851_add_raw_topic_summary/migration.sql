-- AlterTable
ALTER TABLE "RawForumPost" ADD COLUMN     "needsSummarize" BOOLEAN NOT NULL DEFAULT true;

-- CreateTable
CREATE TABLE "RawTopicSummary" (
    "id" SERIAL NOT NULL,
    "url" TEXT NOT NULL,
    "data" JSONB NOT NULL,
    "lastGeneratedAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "RawTopicSummary_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "RawTopicSummary_url_key" ON "RawTopicSummary"("url");
