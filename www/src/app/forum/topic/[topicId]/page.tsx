"use server";
import prisma from "@/lib/prisma";
import type { Prisma } from "@prisma/client";
import { TopicPage } from "./(components)/topic-page";

export type TopicPageProps = {
  topic: Prisma.TopicGetPayload<{
    include: {
      category: true;
    };
  }>;
};

export default async function Page({ params }: { params: any }) {
  const { topicId } = params;

  const topic = (await prisma.topic.findUnique({
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

  return <TopicPage topic={topic} />;
}
