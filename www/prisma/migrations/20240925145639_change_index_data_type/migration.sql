/*
  Warnings:

  - The `data` column on the `EmbeddingIndex` table would be dropped and recreated. This will lead to data loss if there is data in the column.

*/
-- AlterTable
ALTER TABLE "EmbeddingIndex" DROP COLUMN "data",
ADD COLUMN     "data" BYTEA;
