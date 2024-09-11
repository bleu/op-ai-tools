import type React from "react";

import { useEffect, useRef } from "react";
import { Button } from "../../ui/button";
import { Textarea } from "../../ui/textarea";

export interface EditableMessageProps {
  editMessageContent: string;
  setEditMessageContent: (
    content: string | ((prevMessage: string) => string),
  ) => void;
  handleOnSendEditMessage: () => void;
  setIsEditable: (isEditable: boolean) => void;
}

export const EditableMessage: React.FC<EditableMessageProps> = ({
  editMessageContent,
  setEditMessageContent,
  handleOnSendEditMessage,
  setIsEditable,
}) => {
  const inputRef = useRef<HTMLTextAreaElement>(null);

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

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.select();
    }
  }, []);

  return (
    <div className="flex-col flex-1">
      <Textarea
        value={editMessageContent}
        onChange={(e) => setEditMessageContent(e.target.value)}
        ref={inputRef}
        rows={10}
        onKeyDown={handleKeyPress}
      />
      <div className="flex justify-end space-x-2 mt-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsEditable(false)}
        >
          Cancel
        </Button>
        <Button
          size="sm"
          onClick={handleOnSendEditMessage}
          disabled={!editMessageContent}
        >
          Send
        </Button>
      </div>
    </div>
  );
};
