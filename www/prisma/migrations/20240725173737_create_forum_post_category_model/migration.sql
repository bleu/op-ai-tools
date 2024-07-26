-- CreateTable
CREATE TABLE "ForumPostCategory" (
    "id" SERIAL NOT NULL,
    "external_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "color" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "topic_url" TEXT NOT NULL,

    CONSTRAINT "ForumPostCategory_pkey" PRIMARY KEY ("id")
);
