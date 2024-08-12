import type { Message } from "@/app/data";
import {
  type ChatData,
  generateMessageParams,
  generateMessagesMemory,
} from "@/lib/chat-utils";
import { useCallback, useEffect, useState } from "react";
import { useChatApi } from "./useChatApi";

export function useChatState(
  selectedChat: ChatData,
  onUpdateMessages: (newMessages: Message[]) => void,
) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentMessages, setCurrentMessages] = useState<Message[]>([]);
  const [loadingMessageId, setLoadingMessageId] = useState<string | null>(null);

  const { sendMessage: sendMessageApi } = useChatApi();

  useEffect(() => {
    setCurrentMessages(selectedChat.messages || []);
  }, [selectedChat]);

  const sendMessage = useCallback(
    async (newMessage: Message) => {
      const updatedMessages = [...currentMessages, newMessage];
      setCurrentMessages(updatedMessages);
      onUpdateMessages(updatedMessages);
      setIsStreaming(true);
      setIsTyping(true);

      const assistantMessage = generateMessageParams(
        selectedChat.id,
        "",
        "Optimism GovGPT",
      );

      setLoadingMessageId(assistantMessage.id);
      updatedMessages.push(assistantMessage);
      setCurrentMessages([...updatedMessages]);
      onUpdateMessages([...updatedMessages]);

      try {
        // DO NOT SEND MEMORY FOR NOW
        // const messagesMemory = generateMessagesMemory(currentMessages);
        const messagesMemory = [] as any;

        const response = await sendMessageApi(
          newMessage.message,
          messagesMemory,
        );

        setLoadingMessageId(null);

        updatedMessages[updatedMessages.length - 1].message = Array.isArray(
          response["answer"],
        )
          ? response["answer"].join("\n")
          : response["answer"];
        setCurrentMessages([...updatedMessages]);
        onUpdateMessages([...updatedMessages]);

        setIsStreaming(false);
        setIsTyping(false);
      } catch (error) {
        console.error("Error:", error);
        setIsStreaming(false);
        setIsTyping(false);
        setLoadingMessageId(null);

        updatedMessages[updatedMessages.length - 1] = generateMessageParams(
          selectedChat.id,
          "Sorry, an error occurred while processing your request.",
          "Optimism GovGPT",
        );

        setCurrentMessages([...updatedMessages]);
        onUpdateMessages([...updatedMessages]);
      }
    },
    [currentMessages, onUpdateMessages, sendMessageApi, selectedChat.id],
  );

  const handleRegenerateMessage = useCallback(
    (messageId: string) => {
      const messageIndex = currentMessages.findIndex((m) => m.id === messageId);
      if (messageIndex === -1) return;

      const updatedMessages = currentMessages.slice(0, messageIndex);
      setCurrentMessages(updatedMessages);
      onUpdateMessages(updatedMessages);

      const userMessage = currentMessages[messageIndex - 1];
      if (userMessage) {
        sendMessage(userMessage);
      }
    },
    [currentMessages, onUpdateMessages, sendMessage],
  );

  return {
    isStreaming,
    inputMessage,
    setInputMessage,
    isTyping,
    currentMessages,
    sendMessage,
    handleRegenerateMessage,
    loadingMessageId,
  };
}
