import ChatSidebar from "@/components/chat/chat-sidebar";
import type React from "react";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex max-h-[calc(100dvh-4rem)] w-full overflow-hidden">
      <ChatSidebar />
      <main className="flex flex-1">{children}</main>
    </div>
  );
}
