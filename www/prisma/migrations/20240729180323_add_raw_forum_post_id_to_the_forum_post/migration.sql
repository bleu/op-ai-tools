-- AlterTable
ALTER TABLE "ForumPost" ADD COLUMN     "rawForumPostId" INTEGER;

-- AddForeignKey
ALTER TABLE "ForumPost" ADD CONSTRAINT "ForumPost_rawForumPostId_fkey" FOREIGN KEY ("rawForumPostId") REFERENCES "RawForumPost"("id") ON DELETE SET NULL ON UPDATE CASCADE;
