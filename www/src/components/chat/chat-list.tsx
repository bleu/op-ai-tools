import React, { useEffect, useRef } from "react";

import { Message } from "./message/message";
import { getCurrentChat, useChatStore } from "./use-chat-state";
import { ChatEmptyState } from "./chat-empty-state";

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
      <ChatEmptyState
       onSuggestionClick={handleSuggestionClick}
      />
    );
  }  
  return (
    <div className="flex-col-reverse overflow-scroll px-24">
      {currentMessages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
});
