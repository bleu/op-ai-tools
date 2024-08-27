import type { Message } from "@/app/data";
import type { ChatData } from "@/lib/chat-utils";
import React from "react";
import ChatBottombar from "./chat-bottombar";
import { ChatEmptyState } from "./chat-empty-state";
import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";
import { useChatState } from "./useChatState";

interface ChatProps {
  isMobile: boolean;
  onToggleSidebar: () => void;
}

export function Chat({ isMobile, onToggleSidebar }: ChatProps) {
  const {
    isStreaming,
    inputMessage,
    setInputMessage,
    isTyping,
    currentMessages,
    sendMessage,
    handleOnEditMessage,
    loadingMessageId,
  } = useChatState();

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  const handleSetInputMessage = (
    value: string | ((prevState: string) => string),
  ) => {
    if (typeof value === "function") {
      setInputMessage(value(inputMessage));
    } else {
      setInputMessage(value);
    }
  };

  return (
    <div className="flex flex-col w-full h-full">
      <ChatTopbar
        isTyping={isTyping}
        onToggleSidebar={onToggleSidebar}
        isMobile={isMobile}
      />
      <div className="flex-grow overflow-hidden relative">
        {currentMessages.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <ChatEmptyState onSuggestionClick={handleSuggestionClick} />
          </div>
        ) : (
          <ChatList
            messages={currentMessages}
            isMobile={isMobile}
            isStreaming={isStreaming}
            loadingMessageId={loadingMessageId}
            onEditMessage={handleOnEditMessage}
            onSendMessage={sendMessage}
          />
        )}
      </div>
      <ChatBottombar
        sendMessage={sendMessage}
        isMobile={isMobile}
        isStreaming={isStreaming}
        inputMessage={inputMessage}
        setInputMessage={handleSetInputMessage}
      />
    </div>
  );
}
