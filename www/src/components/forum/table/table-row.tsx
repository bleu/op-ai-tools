import Link from "next/link";
import type React from "react";
import { CATEGORY_COLORS } from "../categoryColors";
import { TopicHeader } from "../topic-header";
import { FILTER_OPTIONS, type Topic } from "./post-options";

export function getColor(categoryValue: string) {
  const categoryLabel = FILTER_OPTIONS.options.find(
    (option) => option.value === categoryValue,
  )?.label;

  if (!categoryLabel) {
    return CATEGORY_COLORS.Others;
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
}: Topic) => {
  return (
    <Link href={`/forum/topic/${id}`}>
      <div className="p-1 md:p-4 rounded-md hover:bg-gray-100">
        <TopicHeader
          id={id}
          title={title}
          username={username}
          createdAt={createdAt}
          lastActivity={lastActivity}
          displayUsername={displayUsername}
          readTime={readTime}
          category={category}
          status={status}
        />
        {about && <p className="text-gray-700 mb-2 mt-4">{about}</p>}
      </div>
    </Link>
  );
};
