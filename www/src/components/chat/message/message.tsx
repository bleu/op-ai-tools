import type React from "react";
import { useState } from "react";

import { CopyCheck, Pencil, ThumbsDown } from "lucide-react";

import type { Message as MessageType } from "@/app/data";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import useMobileStore from "@/states/use-mobile-state";
import { MessageAvatar } from "./message-avatar";
import { MessageContent } from "./message-content";

export interface MessageProps {
  message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const [isEditable, setIsEditable] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const { isMobile } = useMobileStore();

  const handleEditClick = () => {
    setIsEditable(true);
  };

  const isAnswer = message.name === "Optimism GovGPT";

  return (
    <div
      className={cn(
        "flex flex-row gap-2 mt-8",
        isAnswer ? "justify-start" : "justify-end",
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {isAnswer && <MessageAvatar name={message.name} />}

      {!isAnswer && (isHovered || isMobile) && !isEditable && (
        <Button
          variant="ghost"
          className="p-2 mt-4"
          size="sm"
          onClick={handleEditClick}
        >
          <Pencil className="h-3.5 w-3.5" />
        </Button>
      )}
      <MessageContent
        isEditable={isEditable}
        message={message}
        setIsEditable={setIsEditable}
      />
    </div>
  );
};
