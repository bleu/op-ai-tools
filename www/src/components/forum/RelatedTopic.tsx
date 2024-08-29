import React from "react";

export function RelatedTopic() {
  return (
    <div className="flex gap-4">
      <div className="flex flex-1 flex-col p-5 bg-gray-100 rounded-md shadow-lg">
        <p className="mb-2 text-sm font-bold">Daily Digest - 9 Jul 24</p>
        <div className="flex flex-row items-center">
          <div className="w-2 h-2 bg-red-400 rounded" />
          <span className="ml-1 text-xs text-gray-700">Retro Funding</span>
        </div>
        <p className="text-xs leading-4 mt-4 line-clamp-4 text-gray-700">
          Content summarized in one paragraph. Lorem ipsum dolor sit amet,
          consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
          labore et dolore magna Content summarized in one paragraph.
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna
        </p>
      </div>
    </div>
  );
}
