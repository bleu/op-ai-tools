-- CreateTable
CREATE TABLE "RawForumPost" (
    "id" SERIAL NOT NULL,
    "external_id" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "rawData" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "RawForumPost_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "RawForumPost_external_id_key" ON "RawForumPost"("external_id");

-- CreateIndex
CREATE UNIQUE INDEX "RawForumPost_url_key" ON "RawForumPost"("url");
