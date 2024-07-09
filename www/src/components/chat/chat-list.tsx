import type { Message, UserData } from "@/app/data";
import { cn } from "@/lib/utils";
import React, { useEffect, useRef } from "react";
import { Avatar, AvatarImage, BoringAvatar } from "../ui/avatar";
import { FormattedMessage } from "../ui/formatted-message";

interface ChatListProps {
  messages?: Message[];
  selectedUser: UserData;
  isMobile: boolean;
  isStreaming: boolean;
}

export function ChatList({
  messages,
  selectedUser,
  isMobile,
  isStreaming,
}: ChatListProps) {
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!messagesContainerRef.current) return;
    messagesContainerRef.current.scrollTop =
      messagesContainerRef.current.scrollHeight;
  }, [messages]);

  const deduplicateLineBreaks = (message: string) => {
    return message.replace(/\n{3,}/g, "\n\n");
  };

  return (
    <div
      ref={messagesContainerRef}
      className="w-full overflow-y-auto overflow-x-hidden h-full flex flex-col"
    >
      {messages?.map((message, index) => (
        <div
          key={message.id}
          className={cn(
            "flex flex-col gap-2 p-4",
            message.name !== "Optimism GovGPT" ? "items-end" : "items-start"
          )}
        >
          <div className="flex gap-3 items-start">
            {message.name === "Optimism GovGPT" && (
              <Avatar className="flex justify-center items-center mt-1">
                <AvatarImage
                  src="/op-logo.png"
                  alt="Optimism GovGPT"
                  width={6}
                  height={6}
                  className="w-10 h-10"
                />
              </Avatar>
            )}
            <div
              className={cn(
                "p-3 rounded-md max-w-md overflow-hidden",
                "bg-accent"
              )}
            >
              {message.isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse" />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-75" />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-150" />
                </div>
              ) : (
                <FormattedMessage
                  content={deduplicateLineBreaks(message.message)}
                />
              )}
            </div>
            {message.name !== "Optimism GovGPT" && (
              <Avatar className="flex justify-center items-center mt-1">
                <BoringAvatar name={message.name} />
              </Avatar>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
