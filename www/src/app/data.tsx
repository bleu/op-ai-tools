export interface BaseMessage {
  id: string;
  name: string;
  timestamp: number;
  isLoading?: boolean;
}

export interface TextMessage extends BaseMessage {
  message: string;
}

export interface StructuredMessage extends BaseMessage {
  message: {
    answer: string;
    url_supporting: string[];
  };
}

export type Message = TextMessage | StructuredMessage;

// Type guard to check if a message is a StructuredMessage
export function isStructuredMessage(
  message: Message,
): message is StructuredMessage {
  return typeof message.message === "object" && "answer" in message.message;
}
