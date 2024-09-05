"use client";

import ChatBottombar from "@/components/chat/chat-bottombar";
import { ChatList } from "@/components/chat/chat-list";
import React from "react";

export default function Chat() {
  return (
    <div className="flex flex-col-reverse min-w-full">
      <div className="mx-24">
        <ChatBottombar isMobile={false} />
      </div>
      <ChatList />
    </div>
  );
}
