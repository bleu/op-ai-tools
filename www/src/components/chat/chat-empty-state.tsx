import Image from "next/image";
import type React from "react";

import useMobileStore from "@/states/use-mobile-state";
import { Button } from "../ui/button";
import { suggestions } from "./chat-suggestions";

export function ChatEmptyState({
  onSuggestionClick,
}: {
  onSuggestionClick: (suggestion: string) => void;
}) {
  const { isMobile } = useMobileStore();

  return (
    <div className="flex flex-col items-center justify-center h-full p-4">
      <div className="mb-8">
        <Image
          src="/op-logo.svg"
          alt="Optimism logo"
          width={75}
          height={75}
          className="w-[75px] md:w-[100px]"
        />
      </div>
      <h2 className="text-lg md:text-2xl font-bold mb-4 text-center text-chat-secondary">
        {isMobile
          ? "Ask me anything about Optimism Governance"
          : "How can I help you today?"}
      </h2>
      {!isMobile && (
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
      )}
    </div>
  );
}
