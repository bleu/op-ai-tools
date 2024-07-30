"use client";

import Link from "next/link";
import { PropsWithChildren } from "react";
import { Octagram } from "@/components/forum/Octagram";
import { Separator } from "@/components/ui/separator";
import { cn, formatDate } from "@/lib/utils";
import { Feedback } from "@/components/forum/Feedback";
import { getColor } from "@/components/forum/table/table-row";
import { TopicPageProps } from "../page";

const Section = ({ title, children }: PropsWithChildren<{ title: string }>) => (
  <div className="space-y-4">
    <h2 className="text-xl font-semibold">{title}</h2>
    {children}
  </div>
);

export function TopicPage({ topic }: TopicPageProps) {
  return (
    <div className="p-6 space-y-8">
      <div className="flex flex-col">
        <div className="flex justify-between items-center">
          <div className="flex items-center justify-left mb-2 gap-2">
            <h1 className="text-2xl font-semibold">{topic.title}</h1>
            {/* {topic.status && <Badge>{topic.status}</Badge>} */}
          </div>
          <div className="flex items-center text-sm text-gray-500">
            {topic.readTime && (
              <>
                <span>{topic.readTime} read</span>
                <span className="mx-2">•</span>
              </>
            )}
            {topic.createdAt && (
              <>
                <span>{formatDate(topic.createdAt)}</span>
              </>
            )}
            {topic.lastActivity && (
              <>
                <span className="mx-2">•</span>
                <span>Last activity: {formatDate(topic.lastActivity)}</span>
              </>
            )}
          </div>
        </div>
        <div className="font-semibold flex gap-1 items-center">
          <Octagram
            label={topic?.category?.name || ""}
            className={cn(
              { [getColor(topic?.category?.externalId || "all")]: true },
              "size-4 fill-current"
            )}
          />
          <span className="text-muted-foreground">{topic?.category?.name}</span>
          {(topic.displayUsername || topic.username) && (
            <>
              <Separator
                orientation="vertical"
                className="h-4 bg-muted-foreground w-[1.5px]"
              />
              <Link
                href={`https://gov.optimism.io/u/${topic.username}/summary`}
                target="_blank"
                className="text-blue-500 underline"
              >
                {topic.displayUsername || topic.username}
              </Link>
            </>
          )}
        </div>
      </div>

      <Section title="TLDR">
        <div>{topic?.tldr}</div>
      </Section>

      <Separator orientation="horizontal" />

      {/* <Section title="Proposal">
        <p>{topic?.proposal}</p>
      </Section>
      */}

      {topic.firstPost && (
        <Section title="Post Summary">
          <div className="whitespace-pre-line">{topic.firstPost}</div>
        </Section>
      )}

      {topic.reaction && (
        <Section title="Reactions">
          <div className="whitespace-pre-line">{topic.reaction}</div>
        </Section>
      )}

      <div>
        <div className="flex items-center justify-end gap-x-4 text-optimism">
          <Feedback />
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
    </div>
  );
}
