"use client";

import { cn } from "@/lib/utils";
import { useChatStore } from "@/states/use-chat-state";
import { FilePlusIcon, TrashIcon } from "@radix-ui/react-icons";
import { ExternalLink } from "lucide-react";
import Link from "next/link";
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
  };

  return (
    <aside className="w-64 bg-chat-primary flex flex-col h-full">
      <div className="flex items-center justify-between p-4 mt-6 md:mt-0">
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
      <div className="h-screen overflow-y-auto px-4">
        <div className="space-y-3 w-full flex-col">
          {Object.values(chats).map((chat) => (
            <>
              <div
                className={cn(
                  "flex group items-center justify-between px-2 py-1 w-full rounded-lg font-medium text-chat-secondary hover:text-optimism text-sm",
                  selectedChatId === chat.id &&
                    "text-optimism bg-optimism/15 hover:bg-optimism/15",
                )}
                key={chat.id}
              >
                <button
                  type="button"
                  className="flex-grow text-left overflow-hidden"
                  onClick={() => setSelectedChatId(chat.id)}
                >
                  <span className="overflow-hidden line-clamp-1">
                    {chat.messages[0]?.data?.answer || "New chat"}
                  </span>
                </button>
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
              </div>
            </>
          ))}
        </div>
      </div>
      <hr className="border-t border-gray-200 my-4 mx-4" />
      <div className="px-4">
        <h2 className="mb-2 font-semibold">Catch up on OP Governance</h2>
        <Link
          href="/forum"
          target="_blank"
          className={cn(
            "flex items-center gap-3 rounded-lg py-2 transition-all hover:bg-gray-100 text-gray-700 text-sm mb-12",
          )}
        >
          Explore GovSummarizer
          <ExternalLink className="h-5 w-5 md:h-4 md:w-4" />
        </Link>
      </div>
    </aside>
  );
}
