import type React from "react";

import { Button } from "../../ui/button";
import { Textarea } from "../../ui/textarea";

export interface EditableMessageProps {
  editMessageContent: string;
  setEditMessageContent: (content: string) => void;
  handleOnSendEditMessage: () => void;
  setIsEditable: (isEditable: boolean) => void;
}

export const EditableMessage: React.FC<EditableMessageProps> = ({
  editMessageContent,
  setEditMessageContent,
  handleOnSendEditMessage,
  setIsEditable,
}) => (
  <div>
    <Textarea
      value={editMessageContent}
      onChange={(e) => setEditMessageContent(e.target.value)}
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
);
