-- CreateTable
CREATE TABLE "ForumPost" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "url" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "about" TEXT NOT NULL,
    "firstPost" TEXT NOT NULL,
    "reaction" TEXT NOT NULL,
    "overview" TEXT NOT NULL,
    "tldr" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "ForumPost_url_key" ON "ForumPost"("url");
