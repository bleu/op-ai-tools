import React, { useEffect, useRef } from "react";

import { getCurrentChat, useChatStore } from "@/states/use-chat-state";
import { ChatEmptyState } from "./chat-empty-state";
import { Message } from "./message/message";

export const ChatList: React.FC = React.memo(() => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentChat = getCurrentChat();
  const currentMessages = currentChat?.messages || [];
  const setInputMessage = useChatStore.use.setInputMessage();

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }, 100);

    return () => clearTimeout(timer);
  }, [currentMessages]);

  if (currentMessages.length === 0) {
    return (
      <div className="flex-1">
        <ChatEmptyState onSuggestionClick={handleSuggestionClick} />
      </div>
    );
  }
  return (
    <div className="flex-col-reverse overflow-y-auto px-6 md:px-8 pb-3 md:pb-6">
      {currentMessages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
});
