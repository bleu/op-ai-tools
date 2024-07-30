"use server";
import prisma from "@/lib/prisma";
import { TopicPage } from "./(components)/topic-page";
import { Prisma } from "@prisma/client";
import { TopicTracker } from "@/components/forum/topic-tracker";

export type TopicPageProps = {
  topic: Prisma.ForumPostGetPayload<{
    include: {
      category: true;
    };
  }>;
};

export default async function Page({ params }: { params: any }) {
  const { topicId } = params;

  const topic = (await prisma.forumPost.findUnique({
    where: {
      id: Number(topicId),
    },
    include: {
      category: {
        select: {
          id: true,
          name: true,
          externalId: true,
        },
      },
    },
  })) as TopicPageProps["topic"];

  return (
    <TopicTracker topic={topic}>
      <TopicPage topic={topic} />
    </TopicTracker>
  );
}
