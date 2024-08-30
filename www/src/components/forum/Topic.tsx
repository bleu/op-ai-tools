import React from "react";

export interface TopicContent {
  id: number;
  title: string;
  about: string | null;
}

export interface TopicProps {
  item: TopicContent;
}

export function Topic({ item }: TopicProps) {
  return (
    <div className="flex flex-col h-full bg-muted border-2 rounded-lg shadow-md p-4 m-0 max-w-xs sm:max-w-xs">
      <h3 className="text-sm font-semibold text-foreground mb-2 line-clamp-1">
        {item.title}
      </h3>
      <p className="text-xs line-clamp-5 text-gray-700">{item.about}</p>
    </div>
  );
}
