import { Octagram } from "@/components/forum/Octagram";
import { cn } from "@/lib/utils";
import Link from "next/link";
import React from "react";
import { ForumPost } from "./post-options";

const CATEGORY_COLORS = {
  all: "text-[#505050]",
  discussion: "text-[#B0B0B0]",
  informative: "text-[#C0392B]",
  feedback: "text-[#E74C3C]",
  announcement: "text-[#E67E22]",
  unimportant: "text-[#F39C12]",
  guide: "text-[#F1C40F]",
};

export const SnapshotProposal = ({
  about,
  id,
  status,
  category,
  author,
  tldr,
  readTime,
  created_at,
  lastActivity,
}: ForumPost) => {
  return (
    <Link href={`/forum/topic/${id}`}>
    <div className="p-4 max-w-7xl mx-auto rounded-md hover:bg-gray-100">
      <div className="flex items-center justify-left mb-2 gap-2">
        <h1 className="text-2xl font-semibold">{about}</h1>
        <span className="bg-yellow-200 text-yellow-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded-md">
          {status}
        </span>
      </div>
      <div className="flex items-center text-sm mb-4">
        <div className="font-semibold flex gap-1 items-center">
          <Octagram
            label={category}
            className={cn(
              /* @ts-ignore-next-line */
              { [CATEGORY_COLORS[category]]: true },
              "size-4 fill-current"
            )}
          />
          <span className="text-muted-foreground">{category}</span>
        </div>
        <span className="mx-2">|</span>
        <a href="#" className="text-blue-600">
          {author}
        </a>
      </div>
      <p className="text-gray-700 mb-4">{tldr}</p>
      <div className="flex items-center text-xs text-gray-500">
        <span>{readTime}</span>
        <span className="mx-2">•</span>
        <span>{created_at}</span>
        <span className="mx-2">•</span>
        <span>{lastActivity}</span>
      </div>
    </div>
    </Link>
    
  );
};
