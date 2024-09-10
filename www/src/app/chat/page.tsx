"use client";

import ChatBottombar from "@/components/chat/chat-bottombar";
import { ChatList } from "@/components/chat/chat-list";
import useMobileStore from "@/states/use-mobile-state";
import React from "react";

export default function Chat() {
  const { isMobile } = useMobileStore();

  return (
    <div className="flex flex-col-reverse min-w-full">
      <div className={isMobile ? "mx-3" : "mx-12"}>
        <ChatBottombar />
      </div>
      <ChatList />
    </div>
  );
}
