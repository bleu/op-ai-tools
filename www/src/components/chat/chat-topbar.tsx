import type { UserData } from "@/app/data";
import { cn } from "@/lib/utils";
import { Info, Phone, Video } from "lucide-react";
import Link from "next/link";
import React from "react";
import { Avatar, AvatarImage, BoringAvatar } from "../ui/avatar";
import { buttonVariants } from "../ui/button";

interface ChatTopbarProps {
  selectedUser: UserData;
}

export default function ChatTopbar({ selectedUser }: ChatTopbarProps) {
  return (
    <div className="w-full h-20 flex p-4 justify-between items-center border-b">
      <div className="flex items-center gap-2">
        <Avatar className="flex justify-center items-center">
          {selectedUser.avatar ? (
            <AvatarImage
              src={selectedUser.avatar}
              alt={selectedUser.name}
              width={6}
              height={6}
              className="w-10 h-10 "
            />
          ) : (
            <BoringAvatar name={selectedUser.name} />
          )}
        </Avatar>
        <div className="flex flex-col">
          <span className="font-medium">{selectedUser.name}</span>
        </div>
      </div>
    </div>
  );
}
