"use client";

import { useChatStore } from "@/states/use-chat-state";
import { FilePlusIcon } from "lucide-react";
import Image from "next/image";
import { Button } from "../ui/button";
import { ChatMobileSidebar } from "./chat-mobile-sidebar";

export function ChatHeader() {
  const { addChat } = useChatStore();

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-4 lg:h-[60px] lg:px-6">
      <div className="md:hidden flex-1">
        <ChatMobileSidebar />
      </div>
      <div>
        <div className="flex flex-1 gap-x-1">
          <Image
            src="/optimism.svg"
            alt="logo"
            width={100}
            height={100}
            className="w-[100px] md:w-[150px]"
          />
          <span className="text-xs md:text-sm font-medium">GovGPT</span>
        </div>
      </div>
      <div className="flex flex-1 justify-end  md:hidden">
        <Button
          className="p-2 hover:bg-optimism/15 ml-auto"
          variant="link"
          onClick={addChat}
        >
          <FilePlusIcon color="#FF0420" className="w-6 h-6" />
        </Button>
      </div>
    </header>
  );
}
