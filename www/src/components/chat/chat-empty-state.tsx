import type React from "react";
import Image from "next/image";

import { Button } from "../ui/button";
import { suggestions } from "./chat-suggestions";

export function ChatEmptyState({
  onSuggestionClick,
}: {
  onSuggestionClick: (suggestion: string) => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center h-full p-4">
      <div className="mb-8">
      <Image
            src="/op-logo.svg"
            alt="Optimism logo"
            width={100}
            height={100}
          />
      </div>
      <h2 className="text-xl md:text-2xl font-bold mb-4 text-center text-chat-secondary">
        How can I help you today?
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
        {suggestions.map((suggestion) => (
          <Button
            key={suggestion.label}
            variant="outline"
            className="flex items-center justify-start gap-2 h-auto py-3 px-4 text-sm md:text-base"
            onClick={() => onSuggestionClick(suggestion.value)}
          >
            {suggestion.icon}
            <span>{suggestion.label}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}
