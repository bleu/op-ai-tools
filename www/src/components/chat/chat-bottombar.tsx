import { generateMessageParams } from "@/lib/chat-utils";
import { cn } from "@/lib/utils";
import { useChatInputRefStore } from "@/states/use-chat-input";
import { getCurrentChat, useChatStore } from "@/states/use-chat-state";
import { SendHorizontal } from "lucide-react";
import Link from "next/link";
import type React from "react";
import { useEffect, useRef } from "react";
import { buttonVariants } from "../ui/button";
import { Textarea } from "../ui/textarea";

export default function ChatBottombar() {
  const inputMessage = useChatStore.use.inputMessage();
  const setInputMessage = useChatStore.use.setInputMessage();
  const isStreaming = useChatStore.use.isStreaming();
  const sendMessage = useChatStore.use.sendMessage();
  const currentChat = getCurrentChat();
  const inputMessageRef = useChatInputRefStore((store) => store.internalRef);

  useEffect(() => {
    if (inputMessageRef?.current) {
      inputMessageRef?.current.focus();
    }
  }, []);

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputMessage(event.target.value);
  };

  const handleSend = () => {
    if (inputMessage.trim() && !isStreaming && currentChat) {
      const newMessage = generateMessageParams(
        currentChat.id,
        { answer: inputMessage.trim(), url_supporting: [] },
        "anonymous",
      );

      sendMessage(newMessage);
      setInputMessage("");

      if (inputMessageRef?.current) {
        inputMessageRef?.current.focus();
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
    <div className="pb-2 flex justify-between w-full items-center gap-2 mb-6">
      <div className="w-full relative flex items-center">
        <Textarea
          autoComplete="off"
          value={inputMessage}
          ref={inputMessageRef}
          onKeyDown={handleKeyPress}
          onChange={handleInputChange}
          name="message"
          placeholder="Message GovGPT"
          className="w-full border rounded-full flex items-center h-12 resize-none overflow-hidden bg-background py-3 pr-10"
          disabled={isStreaming}
        />
        <Link
          href="#"
          className={cn(
            buttonVariants({ variant: "ghost", size: "icon" }),
            "absolute right-2 top-1/2 transform -translate-y-1/2",
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
    </div>
  );
}
