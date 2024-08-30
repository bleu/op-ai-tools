"use client";

import { Feedback } from "@/components/forum/Feedback";
import type { TopicContent } from "@/components/forum/Topic";
import { RelatedTopicCarousel } from "@/components/forum/TopicCarrousel";
import { TopicHeader } from "@/components/forum/topic-header";
import { Separator } from "@/components/ui/separator";
import Link from "next/link";
import type { PropsWithChildren } from "react";
import type { TopicPageProps } from "../page";
import { useUserAccessedTopicPosthogTracker } from "./useUserAccessedTopicPosthogTracker";

const Section = ({ title, children }: PropsWithChildren<{ title: string }>) => (
  <div className="space-y-4">
    <h2 className="text-xl font-semibold">{title}</h2>
    {children}
  </div>
);

export function TopicPage({ topic }: TopicPageProps) {
  useUserAccessedTopicPosthogTracker(topic);

  console.log("TopicPage", topic);

  return (
    <div className="p-1 md:p-4 space-y-8">
      <TopicHeader
        id={topic.id}
        title={topic.title}
        username={topic.username}
        createdAt={topic.createdAt.toISOString()}
        lastActivity={topic.lastActivity?.toISOString()}
        displayUsername={topic.displayUsername}
        readTime={topic.readTime as string}
        category={topic.category as any}
      />

      <Section title="TLDR">
        <div>{topic?.tldr}</div>
      </Section>

      <Separator orientation="horizontal" />

      {/* <Section title="Proposal">
        <p>{topic?.proposal}</p>
      </Section>
      */}

      {topic.firstPost && (
        <Section title="What's Being Discussed">
          <div className="whitespace-pre-line">{topic.firstPost}</div>
        </Section>
      )}

      {topic.overview && (
        <Section title="Overview">
          <div className="whitespace-pre-line">{topic.overview}</div>
        </Section>
      )}

      {topic.reaction && (
        <Section title="Community">
          <div className="whitespace-pre-line">{topic.reaction}</div>
        </Section>
      )}

      <div>
        <div className="flex items-center justify-end gap-x-4 text-optimism">
          <Feedback
            id={topic.id}
            title={topic.title}
            categoryId={topic.category?.id}
            url={topic.url}
          />
        </div>
        <Separator orientation="horizontal" />
      </div>

      <Section title="Original content">
        <Link
          target="_blank"
          href={topic.url}
          className="text-blue-500 underline underline-offset-2"
          prefetch={false}
        >
          gov.optimism.io
        </Link>
      </Section>
      <div>
        <div className="max-w-sm sm:max-w-2xl md:max-w-[83rem]">
          <RelatedTopicCarousel relatedTopics={topic.relatedTopics} />
        </div>
      </div>
    </div>
  );
}
