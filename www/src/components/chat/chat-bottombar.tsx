import { generateMessageParams } from "@/lib/chat-utils";
import { cn } from "@/lib/utils";
import { SendHorizontal } from "lucide-react";
import Link from "next/link";
import type React from "react";
import { useEffect, useRef } from "react";
import { buttonVariants } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { getCurrentChat, useChatStore } from "./use-chat-state";

interface ChatBottombarProps {
  isMobile: boolean;
}

export default function ChatBottombar({ isMobile }: ChatBottombarProps) {
  const inputMessage = useChatStore.use.inputMessage();
  const setInputMessage = useChatStore.use.setInputMessage();
  const isStreaming = useChatStore.use.isStreaming();
  const sendMessage = useChatStore.use.sendMessage();
  const currentChat = getCurrentChat();
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputMessage(event.target.value);
  };

  const handleSend = () => {
    if (inputMessage.trim() && !isStreaming && currentChat) {
      const newMessage = generateMessageParams(
        currentChat.id,
        inputMessage.trim(),
        "anonymous",
      );

      sendMessage(newMessage);
      setInputMessage("");

      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }

    if (event.key === "Enter" && event.shiftKey) {
      event.preventDefault();
      setInputMessage((prev) => `${prev}\n`);
    }
  };

  return (
    <div className="p-2 flex justify-between w-full items-center gap-2">
      <div className="w-full relative">
        <Textarea
          autoComplete="off"
          value={inputMessage}
          ref={inputRef}
          onKeyDown={handleKeyPress}
          onChange={handleInputChange}
          name="message"
          placeholder="Message GovGPT"
          className="w-full border rounded-full flex items-center h-9 resize-none overflow-hidden bg-background"
          disabled={isStreaming}
        />
      </div>
      <Link
        href="#"
        className={cn(
          buttonVariants({ variant: "ghost", size: "icon" }),
          "h-9 w-9",
          "dark:bg-muted dark:text-muted-foreground dark:hover:bg-muted dark:hover:text-white shrink-0",
          {
            "opacity-40": !inputMessage.trim() || isStreaming,
          },
        )}
        onClick={handleSend}
      >
        <SendHorizontal size={20} className="text-muted-foreground" />
      </Link>
    </div>
  );
}
