"use client";

import { ChatHeader } from "@/components/chat/chat-header";
import ChatSidebar from "@/components/chat/chat-sidebar";
import type React from "react";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex-1">
      <ChatHeader />
      <div className="flex max-h-[calc(100dvh-4rem)] w-full overflow-hidden h-full">
        <div className="hidden md:flex">
        <ChatSidebar />
        </div>

        <main className="flex flex-1">{children}</main>
      </div>
    </div>
  );
}
