import { Octagram } from "@/components/forum/Octagram";
import { cn, formatDate } from "@/lib/utils";
import Link from "next/link";
import React from "react";
import { FILTER_OPTIONS, ForumPost } from "./post-options";
import { Badge } from "@/components/ui/badge";
import { CATEGORY_COLORS } from "../categoryColors";
import { Separator } from "@/components/ui/separator";
import { TopicLink } from "@/components/forum/topic-link";

export function getColor(categoryValue: string) {
  const categoryLabel = FILTER_OPTIONS.options.find(
    (option) => option.value === categoryValue
  )?.label;

  if (!categoryLabel) {
    return CATEGORY_COLORS["Others"];
  }

  // @ts-ignore
  return CATEGORY_COLORS[categoryLabel];
}

export const SnapshotProposal = ({
  id,
  title,
  username,
  about,
  createdAt,
  lastActivity,
  displayUsername,
  readTime,
  category,
  status,
}: ForumPost) => {
  return (
    <TopicLink
      id={id}
      title={title}
      category={
        category as {
          externalId: string;
          name: string;
          id: number;
        }
      }
    >
      <div className="p-4 max-w-7xl mx-auto rounded-md hover:bg-gray-100">
        <div className="flex justify-between items-center">
          <div className="flex items-center justify-left mb-2 gap-2">
            <h1 className="text-2xl font-semibold">{title}</h1>
            {status && <Badge>{status}</Badge>}
          </div>
          <div className="flex items-center text-sm text-gray-500">
            {readTime && (
              <>
                <span>{readTime} read</span>
                <span className="mx-2">•</span>
              </>
            )}
            {createdAt && (
              <>
                <span>{formatDate(createdAt)}</span>
              </>
            )}
            {lastActivity && (
              <>
                <span className="mx-2">•</span>
                <span>Last activity: {formatDate(lastActivity)}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex items-center text-sm mb-4">
          <div className="font-semibold flex gap-1 items-center">
            <Octagram
              label={category?.name}
              className={cn(
                /* @ts-ignore-next-line */
                { [getColor(category?.externalId)]: true },
                "size-4 fill-current"
              )}
            />
            <span className="text-muted-foreground">{category?.name}</span>
            {(displayUsername || username) && (
              <>
                <Separator
                  orientation="vertical"
                  className="h-4 bg-muted-foreground w-[1.5px]"
                />
                <Link
                  href={`https://gov.optimism.io/u/${username}/summary`}
                  target="_blank"
                  className="text-blue-500 underline"
                  onClick={(event: React.MouseEvent) => {
                    event.stopPropagation();
                  }}
                >
                  {displayUsername || username}
                </Link>
              </>
            )}
          </div>
        </div>
        {about && <p className="text-gray-700 mb-2">{about}</p>}
      </div>
    </TopicLink>
  );
};
