/*
  Warnings:

  - You are about to drop the `EmbeddingIndex` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Embeddings` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "EmbeddingIndex";

-- DropTable
DROP TABLE "Embeddings";

-- CreateTable
CREATE TABLE "FaissIndex" (
    "id" SERIAL NOT NULL,
    "objectKey" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "FaissIndex_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ManagedIndex" (
    "id" SERIAL NOT NULL,
    "jsonObjectKey" TEXT NOT NULL,
    "compressedObjectKey" TEXT NOT NULL,
    "indexType" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ManagedIndex_pkey" PRIMARY KEY ("id")
);
