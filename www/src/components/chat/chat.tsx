import type { Message, User } from "@/app/data";
import { FileText, HelpCircle, PieChart, Vote } from "lucide-react";
import React from "react";
import ChatBottombar from "./chat-bottombar";
import { ChatEmptyState } from "./chat-emptystate";
import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";
import { useChatState } from "./useChatState";

interface ChatProps {
  selectedChat: User;
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
  } = useChatState(selectedChat, onUpdateMessages);

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  const suggestions = [
    {
      icon: <FileText size={20} />,
      text: "Explain recent proposal",
      onClick: () =>
        handleSuggestionClick(
          "Can you explain the most recent Optimism governance proposal?"
        ),
    },
    {
      icon: <Vote size={20} />,
      text: "How to vote",
      onClick: () =>
        handleSuggestionClick(
          "How can I participate in voting on Optimism governance proposals?"
        ),
    },
    {
      icon: <PieChart size={20} />,
      text: "OP token distribution",
      onClick: () =>
        handleSuggestionClick(
          "Can you give me an overview of the OP token distribution?"
        ),
    },
    {
      icon: <HelpCircle size={20} />,
      text: "Optimism Collective",
      onClick: () =>
        handleSuggestionClick(
          "What is the Optimism Collective and how does it work?"
        ),
    },
  ];

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
            <ChatEmptyState suggestions={suggestions} />
          </div>
        ) : (
          <ChatList
            messages={currentMessages}
            selectedUser={selectedChat}
            isMobile={isMobile}
            isStreaming={isStreaming}
            onRegenerateMessage={handleRegenerateMessage}
          />
        )}
      </div>
      <ChatBottombar
        sendMessage={sendMessage}
        isMobile={isMobile}
        isStreaming={isStreaming}
        inputMessage={inputMessage}
        setInputMessage={setInputMessage}
      />
    </div>
  );
}
