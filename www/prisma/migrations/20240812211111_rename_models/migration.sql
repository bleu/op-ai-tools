/*
  Warnings:

  - You are about to drop the `ForumPost` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `ForumPostCategory` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `RawForumPost` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "ForumPost" DROP CONSTRAINT "ForumPost_categoryId_fkey";

-- DropForeignKey
ALTER TABLE "ForumPost" DROP CONSTRAINT "ForumPost_rawForumPostId_fkey";

-- DropForeignKey
ALTER TABLE "ForumPost" DROP CONSTRAINT "ForumPost_snapshotProposalId_fkey";

-- DropTable
DROP TABLE "ForumPost";

-- DropTable
DROP TABLE "ForumPostCategory";

-- DropTable
DROP TABLE "RawForumPost";

-- CreateTable
CREATE TABLE "Topic" (
    "id" SERIAL NOT NULL,
    "externalId" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "username" TEXT NOT NULL,
    "displayUsername" TEXT NOT NULL,
    "categoryId" INTEGER,
    "rawTopicId" INTEGER,
    "snapshotProposalId" INTEGER,
    "about" TEXT,
    "firstPost" TEXT,
    "reaction" TEXT,
    "overview" TEXT,
    "tldr" TEXT,
    "classification" TEXT,
    "lastActivity" TIMESTAMP(3),
    "readTime" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Topic_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TopicCategory" (
    "id" SERIAL NOT NULL,
    "externalId" TEXT NOT NULL,
    "name" TEXT,
    "color" TEXT,
    "slug" TEXT,
    "description" TEXT,
    "topicUrl" TEXT,
    "filterable" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "TopicCategory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "RawTopic" (
    "id" SERIAL NOT NULL,
    "externalId" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "rawData" JSONB NOT NULL,
    "lastUpdatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "needsSummarize" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "RawTopic_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Topic_externalId_key" ON "Topic"("externalId");

-- CreateIndex
CREATE UNIQUE INDEX "Topic_url_key" ON "Topic"("url");

-- CreateIndex
CREATE UNIQUE INDEX "Topic_snapshotProposalId_key" ON "Topic"("snapshotProposalId");

-- CreateIndex
CREATE UNIQUE INDEX "TopicCategory_externalId_key" ON "TopicCategory"("externalId");

-- CreateIndex
CREATE UNIQUE INDEX "RawTopic_externalId_key" ON "RawTopic"("externalId");

-- CreateIndex
CREATE UNIQUE INDEX "RawTopic_url_key" ON "RawTopic"("url");

-- AddForeignKey
ALTER TABLE "Topic" ADD CONSTRAINT "Topic_categoryId_fkey" FOREIGN KEY ("categoryId") REFERENCES "TopicCategory"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Topic" ADD CONSTRAINT "Topic_rawTopicId_fkey" FOREIGN KEY ("rawTopicId") REFERENCES "RawTopic"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Topic" ADD CONSTRAINT "Topic_snapshotProposalId_fkey" FOREIGN KEY ("snapshotProposalId") REFERENCES "SnapshotProposal"("id") ON DELETE SET NULL ON UPDATE CASCADE;
