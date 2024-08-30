import React from "react";

export interface TopicContent {
  title: string;
  about: string;
  description: string;
}

export interface TopicProps {
  item: TopicContent;
}

export function Topic({ item }: TopicProps) {
  return (
    <div className="flex flex-col bg-muted border-2 rounded-lg shadow-md p-4 m-0 max-w-xs sm:max-w-xs">
      <h3 className="text-sm font-semibold text-foreground mb-2">
        {item.title}
      </h3>
      <p className="text-xs leading-4 line-clamp-4 text-gray-700">
        {item.about}
      </p>
    </div>
  );
}
