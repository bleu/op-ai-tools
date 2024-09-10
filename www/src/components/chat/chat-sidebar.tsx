"use client";

import { cn } from "@/lib/utils";
import { useChatStore } from "@/states/use-chat-state";
import { FilePlusIcon, TrashIcon } from "@radix-ui/react-icons";
import type React from "react";
import { Button } from "../ui/button";

export default function ChatSidebar() {
  const { chats, selectedChatId, setSelectedChatId, addChat, removeChat } =
    useChatStore();

  const handleRemoveChat = (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
    id: string,
  ) => {
    e.stopPropagation();
    removeChat(id);
    if (Object.values(chats).length === 1) {
      addChat();
    }
  };

  return (
    <aside className="w-64 bg-chat-primary flex flex-col h-full">
      <div className="flex items-center justify-between  p-5">
        <h2 className="font-bold text-lg">
          Chats ({Object.values(chats).length})
        </h2>
        <Button
          className="p-2 hover:bg-optimism/15"
          variant="link"
          onClick={addChat}
        >
          <FilePlusIcon color="#FF0420" className="w-6 h-6" />
        </Button>
      </div>
      <div className="h-screen overflow-y-auto">
        <div className="space-y-2 p-5 w-full flex-col">
          {Object.values(chats).map((chat) => (
            <>
              <button
                type="button"
                className={cn(
                  "flex group items-center justify-between  px-2 py-1 w-full rounded-lg font-medium text-chat-secondary hover:text-optimism  text-sm text-left",
                  selectedChatId === chat.id &&
                    "text-optimism bg-optimism/15 hover:bg-optimism/15",
                )}
                key={chat.id}
                onClick={() => setSelectedChatId(chat.id)}
              >
                <span className="overflow-hidden line-clamp-1">
                  {chat.messages[0]?.data?.answer || "New chat"}
                </span>
                <Button
                  className="p-1 ml-1 hover:bg-optimism/15"
                  size="sm"
                  variant="link"
                  onClick={(e) => handleRemoveChat(e, chat.id)}
                >
                  <TrashIcon
                    className={cn(
                      "group-hover:opacity-100 text-optimism opacity-0 w-5 h-5",
                      selectedChatId === chat.id && "opacity-100",
                    )}
                  />
                </Button>
              </button>
            </>
          ))}
        </div>
      </div>
    </aside>
  );
}
