-- CreateTable
CREATE TABLE "AgoraProposal" (
    "id" SERIAL NOT NULL,
    "externalId" TEXT NOT NULL,
    "proposer" TEXT NOT NULL,
    "snapshotBlockNumber" INTEGER NOT NULL,
    "createdTime" TIMESTAMP(3) NOT NULL,
    "startTime" TIMESTAMP(3) NOT NULL,
    "endTime" TIMESTAMP(3) NOT NULL,
    "cancelledTime" TIMESTAMP(3),
    "executedTime" TIMESTAMP(3),
    "markdownTitle" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "quorum" TEXT NOT NULL,
    "approvalThreshold" TEXT,
    "proposalData" JSONB NOT NULL,
    "unformattedProposalData" TEXT NOT NULL,
    "proposalResults" JSONB NOT NULL,
    "proposalType" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "createdTransactionHash" TEXT,
    "cancelledTransactionHash" TEXT,
    "executedTransactionHash" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "AgoraProposal_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "AgoraProposal_externalId_key" ON "AgoraProposal"("externalId");
