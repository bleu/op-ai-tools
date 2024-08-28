"use client";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { cn } from "@/lib/utils";
import React, { useEffect, useState, useCallback } from "react";
import { Sidebar } from "../sidebar";
import { Chat } from "./chat";
import { useChatStore } from "./use-chat-state";

interface ChatLayoutProps {
  defaultLayout?: number[] | undefined;
  defaultCollapsed?: boolean;
  navCollapsedSize?: number;
}

export function ChatLayout({
  defaultLayout = [320, 480],
  defaultCollapsed = true,
  navCollapsedSize,
}: ChatLayoutProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const { chats, selectedChatId, setSelectedChatId, addChat, removeChat } =
    useChatStore();
  const [isMobile, setIsMobile] = useState(false);
  const [showSidebar, setShowSidebar] = useState(!isMobile);

  useEffect(() => {
    const checkScreenWidth = () => {
      const newIsMobile = window.innerWidth <= 768;
      setIsMobile(newIsMobile);
      setShowSidebar(!newIsMobile);
    };
    checkScreenWidth();
    window.addEventListener("resize", checkScreenWidth);
    return () => window.removeEventListener("resize", checkScreenWidth);
  }, []);

  useEffect(() => {
    if (Object.keys(chats).length === 0) {
      addChat();
    }
  }, [addChat, chats]);

  const handleNewChat = useCallback(() => {
    addChat();
    if (isMobile) {
      setShowSidebar(false);
    }
  }, [isMobile, addChat]);

  const toggleSidebar = useCallback(() => {
    setShowSidebar((prev) => !prev);
  }, []);

  return (
    <ResizablePanelGroup
      direction="horizontal"
      onLayout={(sizes: number[]) => {
        document.cookie = `react-resizable-panels:layout=${JSON.stringify(
          sizes,
        )}`;
      }}
      className="h-full items-stretch"
    >
      {(showSidebar || !isMobile) && (
        <ResizablePanel
          defaultSize={defaultLayout[0]}
          collapsedSize={navCollapsedSize}
          collapsible={!isMobile}
          minSize={isMobile ? 100 : 24}
          maxSize={isMobile ? 100 : 30}
          onCollapse={() => setIsCollapsed(true)}
          onExpand={() => setIsCollapsed(false)}
          className={cn(
            isCollapsed &&
              "min-w-[50px] md:min-w-[70px] transition-all duration-300 ease-in-out",
            isMobile && "absolute z-10 h-full bg-background",
          )}
        >
          <Sidebar
            isCollapsed={isCollapsed && !isMobile}
            links={Object.values(chats).map((chat) => ({
              id: chat.id,
              messages: chat.messages,
              name: chat.name,
              timestamp: chat.timestamp,
              variant: selectedChatId === chat.id ? "default" : "ghost",
            }))}
            onNewChat={handleNewChat}
            onRemoveChat={removeChat}
            isMobile={isMobile}
          />
        </ResizablePanel>
      )}
      {!isMobile && <ResizableHandle withHandle />}
      <ResizablePanel defaultSize={defaultLayout[1]} minSize={30}>
        {selectedChatId ? (
          <Chat isMobile={isMobile} onToggleSidebar={toggleSidebar} />
        ) : (
          <div className="flex items-center justify-center h-full">
            <p>Select a chat or start a new one</p>
          </div>
        )}
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}
