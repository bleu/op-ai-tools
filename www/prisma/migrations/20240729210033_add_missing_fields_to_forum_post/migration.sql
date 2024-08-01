-- AlterTable
ALTER TABLE "ForumPost" ADD COLUMN     "classification" TEXT,
ADD COLUMN     "lastActivity" TIMESTAMP(3),
ADD COLUMN     "readTime" INTEGER;
