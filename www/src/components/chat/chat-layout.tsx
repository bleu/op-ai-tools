"use client";
import type { Message } from "@/app/data";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import {
  type ChatData,
  addNewChat,
  generateChatParams,
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
  defaultCollapsed = true,
  navCollapsedSize,
}: ChatLayoutProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const [selectedChat, setSelectedChat] = useState<ChatData | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [chats, setChats] = useState<ChatData[]>([]);
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
    const loadedChats = loadChatsFromLocalStorage();
    if (loadedChats.length > 0) {
      setChats(loadedChats);
      setSelectedChat(loadedChats[0]);
    } else {
      handleNewChat();
    }
  }, []);

  const handleNewChat = useCallback(() => {
    const newChat = generateChatParams("chat");

    setChats((prevChats) => {
      const updatedChats = addNewChat(prevChats);
      saveChatsToLocalStorage(updatedChats);
      return updatedChats;
    });
    setSelectedChat(newChat);
    if (isMobile) {
      setShowSidebar(false);
    }
  }, [isMobile]);

  const handleSelectChat = useCallback(
    (id: string) => {
      const selected = chats.find((chat) => chat.id === id);
      if (selected) {
        setSelectedChat(selected);

        if (isMobile) {
          setShowSidebar(false);
        }
      }
    },
    [chats, isMobile]
  );

  const handleRemoveChat = useCallback(
    (id: string) => {
      setChats((prevChats) => {
        const updatedChats = prevChats.filter((chat) => chat.id !== id);
        saveChatsToLocalStorage(updatedChats);

        if (updatedChats.length > 0) {
          setSelectedChat(updatedChats[0]);
        } else {
          setSelectedChat(null);
        }

        return updatedChats;
      });
    },
    [chats, selectedChat]
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

  const toggleSidebar = useCallback(() => {
    setShowSidebar((prev) => !prev);
  }, []);

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
      {(showSidebar || !isMobile) && (
        <ResizablePanel
          defaultSize={defaultLayout[0]}
          collapsedSize={navCollapsedSize}
          collapsible={!isMobile}
          minSize={isMobile ? 100 : 24}
          maxSize={isMobile ? 100 : 30}
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
              "min-w-[50px] md:min-w-[70px] transition-all duration-300 ease-in-out",
            isMobile && "absolute z-10 h-full bg-background"
          )}
        >
          <Sidebar
            isCollapsed={isCollapsed && !isMobile}
            links={chats.map((chat) => ({
              id: chat.id,
              messages: chat.messages,
              name: chat.name,
              timestamp: chat.timestamp,
              variant: selectedChat?.id === chat.id ? "default" : "ghost",
            }))}
            onSelectChat={handleSelectChat}
            onNewChat={handleNewChat}
            onRemoveChat={handleRemoveChat}
            isMobile={isMobile}
          />
        </ResizablePanel>
      )}
      {!isMobile && <ResizableHandle withHandle />}
      <ResizablePanel defaultSize={defaultLayout[1]} minSize={30}>
        {selectedChat ? (
          <Chat
            selectedChat={selectedChat}
            isMobile={isMobile}
            onUpdateMessages={handleUpdateMessages}
            onToggleSidebar={toggleSidebar}
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
