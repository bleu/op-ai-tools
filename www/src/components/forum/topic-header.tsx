import { Octagram } from "@/components/forum/Octagram";
import { getColor } from "@/components/forum/table/table-row";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn, formatDate } from "@/lib/utils";
import Link from "next/link";
import type { Topic } from "./table/post-options";

export function TopicHeader({
  title,
  username,
  createdAt,
  lastActivity,
  displayUsername,
  readTime,
  category,
  status,
}: Topic) {
  return (
    <div className="flex flex-col md:flex-row justify-between items-start">
      <div className="flex flex-col justify-start flex-grow md:w-2/3 mr-7">
        <div className="flex items-center justify-left md:mb-2 gap-2 w-full">
          <h1 className="text-lg md:text-2xl font-semibold">{title}</h1>
          {status && <Badge>{status}</Badge>}
        </div>
        <div className="text-xs mb-1 md:mb-0 md:text-base font-semibold flex gap-1 items-center w-full whitespace-nowrap">
          {category?.name && (
            <>
              <Octagram
                label={category.name}
                className={cn(
                  { [getColor(category.externalId || "")]: true },
                  "size-4 fill-current"
                )}
              />
              <span className="text-muted-foreground w-auto whitespace-nowrap">
                {category.name}
              </span>
            </>
          )}
          {(displayUsername || username) && (
            <>
              <Separator
                orientation="vertical"
                className="h-4 bg-muted-foreground w-[1px] md:w-[1.5px] mx-1"
              />
              <Link
                href={`https://gov.optimism.io/u/${username}/summary`}
                target="_blank"
                className="text-blue-500 underline w-auto whitespace-nowrap"
                onClick={(event) => {
                  event.stopPropagation();
                }}
              >
                {displayUsername || username}
              </Link>
            </>
          )}
        </div>
      </div>
      <div className="flex text-xs md:text-md text-gray-500 w-full md:w-auto justify-start md:justify-end items-center mt-2 md:mt-0">
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
  );
}
