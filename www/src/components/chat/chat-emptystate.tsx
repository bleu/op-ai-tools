import { InfoCircledIcon } from "@radix-ui/react-icons";
import type React from "react";
import { Button } from "../ui/button";

interface Suggestion {
  icon: React.ReactNode;
  text: string;
  onClick: () => void;
}

interface ChatEmptyStateProps {
  suggestions: Suggestion[];
}

export function ChatEmptyState({ suggestions }: ChatEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full p-4">
      <div className="mb-8">
        <InfoCircledIcon className="w-12 h-12" />
      </div>
      <h2 className="text-xl md:text-2xl font-bold mb-4 text-center">
        How can I help you today?
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
        {suggestions.map((suggestion, index) => (
          <Button
            key={suggestion.text}
            variant="outline"
            className="flex items-center justify-start gap-2 h-auto py-3 px-4 text-sm md:text-base"
            onClick={suggestion.onClick}
          >
            {suggestion.icon}
            <span>{suggestion.text}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}
