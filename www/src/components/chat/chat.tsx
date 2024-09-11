import { getCurrentChat, useChatStore } from "@/states/use-chat-state";
import React from "react";
import ChatBottombar from "./chat-bottombar";
import { ChatEmptyState } from "./chat-empty-state";
import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";

interface ChatProps {
  isMobile: boolean;
  onToggleSidebar: () => void;
}

export function Chat({ isMobile, onToggleSidebar }: ChatProps) {
  const isTyping = useChatStore.use.isTyping();
  const setInputMessage = useChatStore.use.setInputMessage();
  const currentChat = getCurrentChat();

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  return (
    <div className="flex flex-col w-full h-full">
      <ChatTopbar
        isTyping={isTyping}
        onToggleSidebar={onToggleSidebar}
        isMobile={isMobile}
      />
      <div className="flex-grow overflow-hidden relative">
        {!currentChat || currentChat.messages.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <ChatEmptyState onSuggestionClick={handleSuggestionClick} />
          </div>
        ) : (
          <ChatList />
        )}
      </div>
      <ChatBottombar />
    </div>
  );
}
