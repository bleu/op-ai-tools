import type { Message, UserData } from "@/app/data";
import { cn } from "@/lib/utils";
import React, { useEffect, useRef } from "react";
import { Avatar, AvatarImage, BoringAvatar } from "../ui/avatar";
import ChatBottombar from "./chat-bottombar";
import { FormattedMessage } from "../ui/formatted-message";

interface ChatListProps {
  messages?: Message[];
  selectedUser: UserData;
  sendMessage: (newMessage: Message) => void;
  isMobile: boolean;
  isStreaming: boolean;
}

export function ChatList({
  messages,
  selectedUser,
  sendMessage,
  isMobile,
  isStreaming,
}: ChatListProps) {
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!messagesContainerRef.current) return;
    messagesContainerRef.current.scrollTop =
      messagesContainerRef.current.scrollHeight;
  }, [messages]);

  const renderMessage = (message: string, isStreaming: boolean) => {
    if (!message && isStreaming) {
      return <span className="animate-pulse">...</span>;
    }

    const words = message.split(" ");
    return words.map((word, index) => (
      <React.Fragment key={index}>
        {word}
        {index < words.length - 1 && " "}
        {index === words.length - 1 && isStreaming && (
          <span className="animate-pulse ml-1">▋</span>
        )}
      </React.Fragment>
    ));
  };

  return (
    <div className="w-full overflow-y-auto overflow-x-hidden h-full flex flex-col">
      <div
        ref={messagesContainerRef}
        className="w-full overflow-y-auto overflow-x-hidden h-full flex flex-col"
      >
        {messages?.map((message, index) => (
          <div
            key={message.id}
            className={cn(
              "flex flex-col gap-2 p-4",
              message.name !== selectedUser.name ? "items-end" : "items-start"
            )}
          >
            <div className="flex gap-3 items-start">
              {message.name === selectedUser.name && (
                <Avatar className="flex justify-center items-center mt-1">
                  {selectedUser.avatar ? (
                    <AvatarImage
                      src={selectedUser.avatar}
                      alt={selectedUser.name}
                      width={6}
                      height={6}
                      className="w-10 h-10"
                    />
                  ) : (
                    <BoringAvatar name={selectedUser.name} />
                  )}
                </Avatar>
              )}
              <div className="bg-accent p-3 rounded-md max-w-md overflow-hidden">
                {renderMessage(
                  message.message,
                  index === messages.length - 1 && isStreaming
                )}
              </div>
              {message.name !== selectedUser.name && (
                <Avatar className="flex justify-center items-center mt-1">
                  {message.avatar ? (
                    <AvatarImage
                      src={message.avatar}
                      alt={message.name}
                      width={6}
                      height={6}
                      className="w-10 h-10"
                    />
                  ) : (
                    <BoringAvatar name={message.name} />
                  )}
                </Avatar>
              )}
            </div>
          </div>
        ))}
      </div>
      <ChatBottombar
        sendMessage={sendMessage}
        isMobile={isMobile}
        isStreaming={isStreaming}
      />
    </div>
  );
}
