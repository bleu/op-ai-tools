import React from "react";

import type { Data, Message } from "@/app/data";
import { FormattedMessage } from "@/components/ui/formatted-message";
import { LoadingIndicator } from "@/components/ui/loading-indicator";
import { formatAnswerWithReferences } from "@/lib/chat-utils";
import { cn } from "@/lib/utils";

import { useChatStore } from "../use-chat-state";
import { EditableMessage } from "./editable-message";
import { MessageActions } from "./message-actions";

export interface MessageContentProps {
  message: Message;
  isEditable: boolean;
  setIsEditable: (isEditable: boolean) => void;
}
export const MessageContent: React.FC<MessageContentProps> = ({
  message,
  isEditable,
  setIsEditable,
}) => {
  const [editMessageContent, setEditMessageContent] = React.useState(
    message.data.answer,
  );
  const sendMessage = useChatStore.use.sendMessage();
  const loadingMessageId = useChatStore.use.loadingMessageId();

  const handleOnSendEditMessage = () => {
    const editedMessage: Message = {
      ...message,
      data: { ...message.data, answer: editMessageContent.trim() },
    };
    sendMessage(editedMessage);
    setIsEditable(false);
  };

  const messageContent = (data: Data) => {
    if (data.url_supporting.length === 0) return data.answer;
    const formattedMessage = formatAnswerWithReferences(data);
    return formattedMessage.replace(/\n/g, "<br />");
  };

  if (loadingMessageId === message.id) {
    return <LoadingIndicator />;
  }

  if (isEditable && message.name !== "Optimism GovGPT") {
    return (
      <EditableMessage
        editMessageContent={editMessageContent}
        setEditMessageContent={setEditMessageContent}
        handleOnSendEditMessage={handleOnSendEditMessage}
        setIsEditable={setIsEditable}
      />
    );
  }

  return (
    <div className={cn("p-3 rounded-md max-w-md overflow-hidden", "bg-accent")}>
      <FormattedMessage content={messageContent(message.data)} />
      <MessageActions message={message} />
    </div>
  );
};
