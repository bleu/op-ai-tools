/*
  Warnings:

  - Added the required column `indexToDocstoreId` to the `Embeddings` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Embeddings" ADD COLUMN     "indexToDocstoreId" JSONB NOT NULL;
