import { Menu } from "lucide-react";
import React from "react";
import { Avatar, AvatarImage } from "../ui/avatar";
import { Button } from "../ui/button";

interface ChatTopbarProps {
  isTyping: boolean;
  onToggleSidebar: () => void;
  isMobile: boolean;
}

export default function ChatTopbar({
  isTyping,
  onToggleSidebar,
  isMobile,
}: ChatTopbarProps) {
  return (
    <div className="w-full h-20 flex items-center p-4 justify-between border-b">
      <div className="flex items-center gap-2">
        {isMobile && (
          <Button variant="ghost" size="icon" onClick={onToggleSidebar}>
            <Menu className="h-5 w-5" />
          </Button>
        )}
        <Avatar className="flex justify-center items-center">
          <AvatarImage
            src="/op-logo.png"
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
