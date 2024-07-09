import React from "react";
import { Avatar, AvatarImage, BoringAvatar } from "../ui/avatar";

interface ChatTopbarProps {
  isTyping: boolean;
}

export default function ChatTopbar({ isTyping }: ChatTopbarProps) {
  return (
    <div className="w-full h-20 flex flex-col p-4 justify-center border-b">
      <div className="flex items-center gap-2">
        <Avatar className="flex justify-center items-center">
          <AvatarImage
            src="/op-logo.png" // Make sure to add the Optimism logo to your public folder
            alt="Optimism GovGPT"
            width={6}
            height={6}
            className="w-10 h-10"
          />
        </Avatar>
        <div className="flex flex-col">
          <span className="font-medium">Optimism GovGPT</span>
          {isTyping && (
            <span className="text-sm text-muted-foreground">typing...</span>
          )}
        </div>
      </div>
    </div>
  );
}
