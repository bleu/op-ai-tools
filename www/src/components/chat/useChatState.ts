import type { Message } from "@/app/data";
import { type ChatData, generateMessageParams } from "@/lib/chat-utils";
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
        const reader = await sendMessageApi(newMessage.message);
        const decoder = new TextDecoder();

        setLoadingMessageId(null);
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          if (chunk.trim() === "[DONE]") {
            setIsStreaming(false);
            setIsTyping(false);
            break;
          }
          if (chunk.startsWith("error:")) {
            console.error("Error from server:", chunk.slice(6));
            setIsStreaming(false);
            setIsTyping(false);
            break;
          }

          updatedMessages[updatedMessages.length - 1].message += chunk;
          setCurrentMessages([...updatedMessages]);
          onUpdateMessages([...updatedMessages]);
        }
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
