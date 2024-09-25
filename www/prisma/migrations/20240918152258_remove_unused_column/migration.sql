/*
  Warnings:

  - You are about to drop the column `indexToDocstoreId` on the `Embeddings` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Embeddings" DROP COLUMN "indexToDocstoreId";
