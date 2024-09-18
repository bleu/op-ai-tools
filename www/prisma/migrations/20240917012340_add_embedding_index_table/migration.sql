-- CreateTable
CREATE TABLE "EmbeddingIndex" (
    "id" SERIAL NOT NULL,
    "data" JSONB NOT NULL,
    "embedData" BYTEA NOT NULL,
    "indexType" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "EmbeddingIndex_pkey" PRIMARY KEY ("id")
);
