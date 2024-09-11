import { Clipboard, ThumbsDown } from "lucide-react";
import type React from "react";

import type { Message } from "@/app/data";
import { Button } from "@/components/ui/button";
import { useCopyMessage } from "@/components/ui/hooks/use-copy-message";
import { useFeedback } from "@/components/ui/hooks/use-feedback";
import { useChatStore } from "@/states/use-chat-state";


export interface MessageActionsProps {
  message: Message;
}

export const MessageActions: React.FC<MessageActionsProps> = ({ message }) => {
  const { handleNegativeReaction, FeedbackDialog } = useFeedback(message);
  const { handleCopyMessage } = useCopyMessage();
  const isStreaming = useChatStore.use.isStreaming();

  if (isStreaming || message.name !== "Optimism GovGPT") {
    return null;
  }

  return (
    <div className="flex">
      <Button
        variant="ghost"
        className="p-2 transition-colors duration-200 hover:bg-chat-primary"
        size="sm"
        onClick={() => handleCopyMessage(message.data.answer)}
      >
        <Clipboard className="h-3.5 w-3.5" />
      </Button>
      <FeedbackDialog
        trigger={
          <Button
            variant="ghost"
            className="transition-colors duration-200 hover:bg-chat-primary"
            size="sm"
            onClick={() => handleNegativeReaction()}
          >
            <ThumbsDown className="h-3.5 w-3.5 " />
          </Button>
        }
      />
    </div>
  );
};
