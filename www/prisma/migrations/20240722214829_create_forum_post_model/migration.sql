-- CreateTable
CREATE TABLE "ForumPost" (
    "id" SERIAL NOT NULL,
    "url" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "about" TEXT NOT NULL,
    "firstPost" TEXT NOT NULL,
    "reaction" TEXT NOT NULL,
    "overview" TEXT NOT NULL,
    "tldr" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ForumPost_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "ForumPost_url_key" ON "ForumPost"("url");
