import type React from "react";

import { Button } from "../../ui/button";
import { Textarea } from "../../ui/textarea";

export interface EditableMessageProps {
  editMessageContent: string;
  setEditMessageContent: (content: string | ((prevMessage: string) => string)) => void;
  handleOnSendEditMessage: () => void;
  setIsEditable: (isEditable: boolean) => void;
}

export const EditableMessage: React.FC<EditableMessageProps> = ({
  editMessageContent,
  setEditMessageContent,
  handleOnSendEditMessage,
  setIsEditable,
}) => {

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleOnSendEditMessage();
    }

    if (event.key === "Enter" && event.shiftKey) {
      event.preventDefault();
      setEditMessageContent((prev) => `${prev}\n`);
    }
  };
  
  return(
  <div>
    <Textarea
      value={editMessageContent}
      onChange={(e) => setEditMessageContent(e.target.value)}
      onKeyDown={handleKeyPress}
      className="min-w-96 "
    />
    <div className="flex justify-end space-x-2 mt-2">
      <Button variant="outline" size="sm" onClick={() => setIsEditable(false)}>
        Cancel
      </Button>
      <Button size="sm" onClick={handleOnSendEditMessage}>
        Send
      </Button>
    </div>
  </div>
)};
