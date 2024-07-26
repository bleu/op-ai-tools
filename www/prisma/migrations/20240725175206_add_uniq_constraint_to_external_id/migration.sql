/*
  Warnings:

  - A unique constraint covering the columns `[external_id]` on the table `ForumPostCategory` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "ForumPostCategory_external_id_key" ON "ForumPostCategory"("external_id");
