import { cn } from "@/lib/utils";
import React from "react";
import { Octagram } from "./Octagram";
import { getColor } from "./table/table-row";

export interface TopicContent {
  id: number;
  title: string;
  about: string | null;
}

export interface Category {
  id: number;
  name?: string;
  externalId: string;
}

export interface TopicProps {
  item: TopicContent;
  category?: Category
}


export function Topic({ item, category }: TopicProps) {
  return (
    <div className="flex flex-col h-full bg-gray-100 rounded-lg border-1 shadow-lg p-4 m-0 max-w-xs sm:max-w-xs">
      <h3 className="text-sm font-semibold text-foreground mb-2 line-clamp-2">
        {item.title}
      </h3>
      {category?.name && (
        <div className="flex flex-row items-center mb-3">
          <Octagram
            label={category.name}
            className={cn(
              { [getColor(category.externalId || "")]: true },
              "size-2 fill-current",
            )}
          />
          <span className="text-muted-foreground text-xs w-auto whitespace-nowrap ml-2 ">
            {category.name}
          </span>
        </div>
      )}
      <p className="text-xs line-clamp-4 text-gray-700">{item.about}</p>
    </div>
  );
}
