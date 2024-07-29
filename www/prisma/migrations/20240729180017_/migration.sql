/*
  Warnings:

  - You are about to drop the column `category` on the `ForumPost` table. All the data in the column will be lost.
  - You are about to drop the column `external_id` on the `ForumPost` table. All the data in the column will be lost.
  - You are about to drop the column `external_id` on the `ForumPostCategory` table. All the data in the column will be lost.
  - You are about to drop the column `topic_url` on the `ForumPostCategory` table. All the data in the column will be lost.
  - You are about to drop the column `external_id` on the `RawForumPost` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[externalId]` on the table `ForumPost` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[externalId]` on the table `ForumPostCategory` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[externalId]` on the table `RawForumPost` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `externalId` to the `ForumPost` table without a default value. This is not possible if the table is not empty.
  - Added the required column `externalId` to the `ForumPostCategory` table without a default value. This is not possible if the table is not empty.
  - Added the required column `externalId` to the `RawForumPost` table without a default value. This is not possible if the table is not empty.

*/
-- DropIndex
DROP INDEX "ForumPost_external_id_key";

-- DropIndex
DROP INDEX "ForumPostCategory_external_id_key";

-- DropIndex
DROP INDEX "RawForumPost_external_id_key";

-- AlterTable
ALTER TABLE "ForumPost" DROP COLUMN "category",
DROP COLUMN "external_id",
ADD COLUMN     "categoryId" INTEGER,
ADD COLUMN     "externalId" TEXT NOT NULL,
ALTER COLUMN "about" DROP NOT NULL,
ALTER COLUMN "firstPost" DROP NOT NULL,
ALTER COLUMN "reaction" DROP NOT NULL,
ALTER COLUMN "overview" DROP NOT NULL,
ALTER COLUMN "tldr" DROP NOT NULL;

-- AlterTable
ALTER TABLE "ForumPostCategory" DROP COLUMN "external_id",
DROP COLUMN "topic_url",
ADD COLUMN     "externalId" TEXT NOT NULL,
ADD COLUMN     "topicUrl" TEXT;

-- AlterTable
ALTER TABLE "RawForumPost" DROP COLUMN "external_id",
ADD COLUMN     "externalId" TEXT NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "ForumPost_externalId_key" ON "ForumPost"("externalId");

-- CreateIndex
CREATE UNIQUE INDEX "ForumPostCategory_externalId_key" ON "ForumPostCategory"("externalId");

-- CreateIndex
CREATE UNIQUE INDEX "RawForumPost_externalId_key" ON "RawForumPost"("externalId");

-- AddForeignKey
ALTER TABLE "ForumPost" ADD CONSTRAINT "ForumPost_categoryId_fkey" FOREIGN KEY ("categoryId") REFERENCES "ForumPostCategory"("id") ON DELETE SET NULL ON UPDATE CASCADE;
