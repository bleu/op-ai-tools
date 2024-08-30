import React from "react";

export interface TopicContent {
  title: string;
  subtitle: string;
  description: string;
}

export interface TopicProps {
  item: TopicContent;
}

export function Topic({ item }: TopicProps) {
  return (
    <div className="flex flex-col bg-gray-100 rounded-lg shadow-md  p-4">
      <h3 className="text-sm font-semibold text-gray-800 mb-2">{item.title}</h3>
      <div className="flex items-center mb-3">
        <div className="w-2 h-2 bg-blue-500 rounded-full mr-2 flex-shrink-0" />
        <span className="text-xs text-gray-600 truncate">{item.subtitle}</span>
      </div>
      <p className="text-xs leading-4 line-clamp-4 text-gray-700">
        {item.description}
      </p>
    </div>
  );
}
