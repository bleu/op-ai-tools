import type { Message } from "@/app/data";
import { type ChatData, generateMessageParams } from "@/lib/chat-utils";
import { cn } from "@/lib/utils";
import { SendHorizontal } from "lucide-react";
import Link from "next/link";
import type React from "react";
import { useEffect, useRef } from "react";
import { buttonVariants } from "../ui/button";
import { Textarea } from "../ui/textarea";

interface ChatBottombarProps {
  sendMessage: (newMessage: Message) => void;
  isMobile: boolean;
  isStreaming: boolean;
  inputMessage: string;
  selectedChat: ChatData;
  setInputMessage: (message: string | ((prev: string) => string)) => void;
}

export default function ChatBottombar({
  sendMessage,
  isMobile,
  isStreaming,
  inputMessage,
  setInputMessage,
  selectedChat,
}: ChatBottombarProps) {
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // biome-ignore lint/correctness/useExhaustiveDependencies: <explanation>
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [inputMessage]);

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputMessage(event.target.value);
  };

  const handleSend = () => {
    if (inputMessage.trim() && !isStreaming) {
      const newMessage: Message = generateMessageParams(
        selectedChat.id,
        inputMessage.trim(),
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
      <div key="input" className="w-full relative">
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
