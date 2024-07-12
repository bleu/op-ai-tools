import type { Message } from "@/app/data";
import type { ChatData } from "@/lib/chat-utils";
import React from "react";
import ChatBottombar from "./chat-bottombar";
import { ChatEmptyState } from "./chat-empty-state";
import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";
import { useChatState } from "./useChatState";

interface ChatProps {
  selectedChat: ChatData;
  isMobile: boolean;
  onUpdateMessages: (newMessages: Message[]) => void;
  onToggleSidebar: () => void;
}

export function Chat({
  selectedChat,
  isMobile,
  onUpdateMessages,
  onToggleSidebar,
}: ChatProps) {
  const {
    isStreaming,
    inputMessage,
    setInputMessage,
    isTyping,
    currentMessages,
    sendMessage,
    handleRegenerateMessage,
    loadingMessageId,
  } = useChatState(selectedChat, onUpdateMessages);

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
        {currentMessages.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <ChatEmptyState onSuggestionClick={handleSuggestionClick} />
          </div>
        ) : (
          <ChatList
            messages={currentMessages}
            selectedChat={selectedChat}
            isMobile={isMobile}
            isStreaming={isStreaming}
            onRegenerateMessage={handleRegenerateMessage}
            loadingMessageId={loadingMessageId}
          />
        )}
      </div>
      <ChatBottombar
        selectedChat={selectedChat}
        sendMessage={sendMessage}
        isMobile={isMobile}
        isStreaming={isStreaming}
        inputMessage={inputMessage}
        setInputMessage={setInputMessage}
      />
    </div>
  );
}
