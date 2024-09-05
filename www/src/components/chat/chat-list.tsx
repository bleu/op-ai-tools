import React, { useEffect, useRef } from "react";

import { CopyCheck, ThumbsDown } from "lucide-react";
import { Button } from "../ui/button";
import { ScrollArea } from "../ui/scroll-area";
import { Message } from "./message/message";
import { MessageAvatar } from "./message/message-avatar";
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
    <div className="flex-col-reverse overflow-scroll px-24">
      {currentMessages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
});
