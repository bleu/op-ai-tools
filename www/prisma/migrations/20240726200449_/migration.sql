/*
  Warnings:

  - A unique constraint covering the columns `[external_id]` on the table `ForumPost` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `displayUsername` to the `ForumPost` table without a default value. This is not possible if the table is not empty.
  - Added the required column `external_id` to the `ForumPost` table without a default value. This is not possible if the table is not empty.
  - Added the required column `title` to the `ForumPost` table without a default value. This is not possible if the table is not empty.
  - Added the required column `username` to the `ForumPost` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "ForumPost" ADD COLUMN     "displayUsername" TEXT NOT NULL,
ADD COLUMN     "external_id" TEXT NOT NULL,
ADD COLUMN     "title" TEXT NOT NULL,
ADD COLUMN     "username" TEXT NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "ForumPost_external_id_key" ON "ForumPost"("external_id");
