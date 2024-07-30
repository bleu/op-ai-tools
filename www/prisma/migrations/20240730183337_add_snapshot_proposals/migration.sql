/*
  Warnings:

  - A unique constraint covering the columns `[snapshotProposalId]` on the table `ForumPost` will be added. If there are existing duplicate values, this will fail.

*/
-- AlterTable
ALTER TABLE "ForumPost" ADD COLUMN     "snapshotProposalId" INTEGER;

-- CreateTable
CREATE TABLE "SnapshotProposal" (
    "id" SERIAL NOT NULL,
    "externalId" TEXT NOT NULL,
    "spaceId" TEXT NOT NULL,
    "spaceName" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "author" TEXT NOT NULL,
    "choices" JSONB NOT NULL,
    "state" TEXT NOT NULL,
    "votes" INTEGER NOT NULL,
    "end" TIMESTAMP(3) NOT NULL,
    "start" TIMESTAMP(3) NOT NULL,
    "type" TEXT NOT NULL,
    "body" TEXT NOT NULL,
    "discussion" TEXT,
    "quorum" DOUBLE PRECISION,
    "quorumType" TEXT,
    "snapshot" TEXT NOT NULL,
    "scores" JSONB NOT NULL,
    "winningOption" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "SnapshotProposal_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "SnapshotProposal_externalId_key" ON "SnapshotProposal"("externalId");

-- CreateIndex
CREATE UNIQUE INDEX "ForumPost_snapshotProposalId_key" ON "ForumPost"("snapshotProposalId");

-- AddForeignKey
ALTER TABLE "ForumPost" ADD CONSTRAINT "ForumPost_snapshotProposalId_fkey" FOREIGN KEY ("snapshotProposalId") REFERENCES "SnapshotProposal"("id") ON DELETE SET NULL ON UPDATE CASCADE;
