-- CreateTable
CREATE TABLE "Embeddings" (
    "id" SERIAL NOT NULL,
    "compressedData" BYTEA NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Embeddings_pkey" PRIMARY KEY ("id")
);
