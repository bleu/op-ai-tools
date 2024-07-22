import { Octagram } from "@/components/forum/Octagram";
import { cn } from "@/lib/utils";
import React from "react";

const CATEGORY_COLORS = {
  All: "text-[#505050]",
  Delegates: "text-[#B0B0B0]",
  "General Discussions": "text-[#C0392B]",
  "Mission Grants": "text-[#E74C3C]",
  "Updates and Announcements": "text-[#E67E22]",
  "Retro Funding": "text-[#F39C12]",
  Others: "text-[#F1C40F]",
};

export const SnapshotProposal = ({
  title,
  status,
  category,
  author,
  summary,
  readTime,
  date,
  lastActivity,
}: {
  title: string;
  status: string;
  category: string;
  author: string;
  summary: string;
  readTime: string;
  date: string;
  lastActivity: string;
}) => {
  return (
    <div className="p-4 max-w-7xl mx-auto">
      <div className="flex items-center justify-left mb-2 gap-2">
        <h1 className="text-2xl font-semibold">{title}</h1>
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
      <p className="text-gray-700 mb-4">{summary}</p>
      <div className="flex items-center text-xs text-gray-500">
        <span>{readTime}</span>
        <span className="mx-2">•</span>
        <span>{date}</span>
        <span className="mx-2">•</span>
        <span>{lastActivity}</span>
      </div>
    </div>
  );
};
