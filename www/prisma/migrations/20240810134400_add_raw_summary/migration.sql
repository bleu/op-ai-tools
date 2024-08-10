-- CreateTable
CREATE TABLE "RawSummary" (
    "id" SERIAL NOT NULL,
    "url" TEXT NOT NULL,
    "data" TEXT NOT NULL,
    "lastGeneratedAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "RawSummary_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "RawSummary_url_key" ON "RawSummary"("url");
