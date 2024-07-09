"use client";

import { type Message, userData } from "@/app/data";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import {
  type ChatData,
  addNewChat,
  getChatName,
  getValidTimestamp,
  loadChatsFromLocalStorage,
  saveChatsToLocalStorage,
} from "@/lib/chat-utils";
import { cn } from "@/lib/utils";
import React, { useEffect, useState, useCallback } from "react";
import { Sidebar } from "../sidebar";
import { Chat } from "./chat";

interface ChatLayoutProps {
  defaultLayout?: number[] | undefined;
  defaultCollapsed?: boolean;
  navCollapsedSize?: number;
}

export function ChatLayout({
  defaultLayout = [320, 480],
  defaultCollapsed = false,
  navCollapsedSize,
}: ChatLayoutProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const [selectedChat, setSelectedChat] = useState<ChatData | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [chats, setChats] = useState<ChatData[]>([]);

  useEffect(() => {
    const checkScreenWidth = () => setIsMobile(window.innerWidth <= 768);
    checkScreenWidth();
    window.addEventListener("resize", checkScreenWidth);
    return () => window.removeEventListener("resize", checkScreenWidth);
  }, []);

  useEffect(() => {
    const loadedChats = loadChatsFromLocalStorage();
    if (loadedChats.length > 0) {
      setChats(loadedChats);
      setSelectedChat(loadedChats[0]);
    } else {
      handleNewChat();
    }
  }, []);

  const handleNewChat = useCallback(() => {
    const newChat: ChatData = {
      id: Date.now(),
      name: "New Chat",
      messages: [],
      timestamp: Date.now(),
    };
    setChats((prevChats) => {
      const updatedChats = [newChat, ...prevChats];
      saveChatsToLocalStorage(updatedChats);
      return updatedChats;
    });
    setSelectedChat(newChat);
  }, []);

  const handleSelectChat = useCallback(
    (id: number) => {
      const selected = chats.find((chat) => chat.id === id);
      if (selected) setSelectedChat(selected);
    },
    [chats]
  );

  const handleUpdateMessages = useCallback(
    (newMessages: Message[]) => {
      if (!selectedChat) return;

      setChats((prevChats) => {
        const updatedChats = prevChats.map((chat) =>
          chat.id === selectedChat.id
            ? {
                ...chat,
                messages: newMessages,
                name: getChatName(newMessages),
                timestamp: getValidTimestamp(
                  newMessages[newMessages.length - 1]?.timestamp
                ),
              }
            : chat
        );
        saveChatsToLocalStorage(updatedChats);
        return updatedChats;
      });
      setSelectedChat((prevSelected) => {
        if (!prevSelected) return null;
        return {
          ...prevSelected,
          messages: newMessages,
          name: getChatName(newMessages),
          timestamp: getValidTimestamp(
            newMessages[newMessages.length - 1]?.timestamp
          ),
        };
      });
    },
    [selectedChat]
  );

  return (
    <ResizablePanelGroup
      direction="horizontal"
      onLayout={(sizes: number[]) => {
        document.cookie = `react-resizable-panels:layout=${JSON.stringify(
          sizes
        )}`;
      }}
      className="h-full items-stretch"
    >
      <ResizablePanel
        defaultSize={defaultLayout[0]}
        collapsedSize={navCollapsedSize}
        collapsible={true}
        minSize={isMobile ? 0 : 24}
        maxSize={isMobile ? 8 : 30}
        onCollapse={() => {
          setIsCollapsed(true);
          document.cookie = "react-resizable-panels:collapsed=true";
        }}
        onExpand={() => {
          setIsCollapsed(false);
          document.cookie = "react-resizable-panels:collapsed=false";
        }}
        className={cn(
          isCollapsed &&
            "min-w-[50px] md:min-w-[70px] transition-all duration-300 ease-in-out"
        )}
      >
        <Sidebar
          isCollapsed={isCollapsed || isMobile}
          links={chats.map((chat) => ({
            id: chat.id,
            name: chat.name,
            timestamp: chat.timestamp,
            variant: selectedChat?.id === chat.id ? "default" : "ghost",
          }))}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
        />
      </ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel defaultSize={defaultLayout[1]} minSize={30}>
        {selectedChat ? (
          <Chat
            selectedChat={selectedChat}
            messages={selectedChat.messages}
            isMobile={isMobile}
            onUpdateMessages={handleUpdateMessages}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <p>Select a chat or start a new one</p>
          </div>
        )}
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}
