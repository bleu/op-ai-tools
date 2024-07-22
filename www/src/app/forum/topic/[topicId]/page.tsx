"use client";

import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { PropsWithChildren, useEffect, useState } from "react";
import { Octagram } from "@/components/forum/Octagram";
import { Separator } from "@/components/ui/separator";
import { fetchData, ForumPost } from "@/components/forum/table/makeForumData";
import { cn, formatDate } from "@/lib/utils";
import { CATEGORY_COLORS } from "@/components/forum/categoryColors";
import { Feedback } from "@/components/forum/Feedback";

const Section = ({ title, children }: PropsWithChildren<{ title: string }>) => (
  <div className="space-y-4">
    <h2 className="text-xl font-semibold">{title}</h2>
    {children}
  </div>
);

export default function TopicPage() {
  const [topicData, setTopicData] = useState<ForumPost>();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      const result = await fetchData(0, 1);
      setTopicData(result.data[0]);
    }
    loadData();
  }, []);

  useEffect(() => {
    if (topicData) {
      setIsLoading(false);
    }
  }, [topicData]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6 space-y-8">
      <div className="space-y-2 flex flex-col md:flex-row justify-between items-start">
        <div className="flex flex-col gap-y-2">
          <div className="flex flex-col md:flex-row md:items-center gap-2">
            <h1 className="text-2xl md:text-3xl font-bold">
              {topicData?.title}
            </h1>
            <Badge variant="secondary" className="w-fit">
              {topicData?.status}
            </Badge>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <Octagram
              label={topicData?.category}
              className={cn(
                /* @ts-ignore-next-line */
                { [CATEGORY_COLORS[topicData?.category]]: true },
                "size-4 fill-current"
              )}
            />
            <span>{topicData?.category}</span>
            <Link
              target="_blank"
              href="#"
              className="text-blue-500 underline underline-offset-2"
              prefetch={false}
            >
              {topicData?.author}
            </Link>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">
            {topicData?.readTime}
          </span>
          <span className="text-sm text-muted-foreground">•</span>
          <span className="text-sm text-muted-foreground">
            {formatDate(topicData?.date)}
          </span>
          <span className="text-sm text-muted-foreground">•</span>
          <span className="text-sm text-muted-foreground">
            Last activity {topicData?.lastActivity}
          </span>
        </div>
      </div>

      <Section title="TLDR">
        <p>{topicData?.summary}</p>
      </Section>

      <Separator orientation="horizontal" />

      <Section title="Proposal">
        <p>{topicData?.proposal}</p>
      </Section>

      <Section title="Some user opinions">
        <ul className="list-disc list-inside">
          {topicData?.userOpinions.map((opinion, index) => (
            <li key={index}>{opinion}</li>
          ))}
        </ul>
      </Section>

      <div>
        <div className="flex items-center justify-end gap-x-4 text-optimism">
          <Feedback />
        </div>
        <Separator orientation="horizontal" />
      </div>

      <Section title="Original content">
        <div className="space-x-4">
          {topicData?.originalContent.map((link, index) => (
            <Link
              target="_blank"
              key={index}
              href={link.url}
              className="text-blue-500 underline underline-offset-2"
              prefetch={false}
            >
              {link.text}
            </Link>
          ))}
        </div>
      </Section>
    </div>
  );
}
