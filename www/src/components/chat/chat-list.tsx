import React, { useEffect, useRef } from "react";

import { ScrollArea } from "../ui/scroll-area";
import { Message } from "./message/message";
import { getCurrentChat } from "./use-chat-state";

export const ChatList: React.FC = React.memo(() => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentChat = getCurrentChat();
  const currentMessages = currentChat?.messages || [];

  useEffect(() => {
    const timer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }, 100);

    return () => clearTimeout(timer);
  }, [currentMessages]);

  return (
    <ScrollArea className="w-full overflow-y-auto overflow-x-hidden h-full flex flex-col absolute">
      {currentMessages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </ScrollArea>
  );
});
