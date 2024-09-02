-- CreateTable
CREATE TABLE "RelatedTopics" (
    "fromTopicId" INTEGER NOT NULL,
    "toTopicId" INTEGER NOT NULL,

    CONSTRAINT "RelatedTopics_pkey" PRIMARY KEY ("fromTopicId","toTopicId")
);

-- AddForeignKey
ALTER TABLE "RelatedTopics" ADD CONSTRAINT "RelatedTopics_fromTopicId_fkey" FOREIGN KEY ("fromTopicId") REFERENCES "Topic"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "RelatedTopics" ADD CONSTRAINT "RelatedTopics_toTopicId_fkey" FOREIGN KEY ("toTopicId") REFERENCES "Topic"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
