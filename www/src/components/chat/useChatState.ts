import { useState, useCallback, useEffect } from "react";
import type { Message, User } from "@/app/data";
import { useChatApi } from "./useChatApi";

export function useChatState(
  selectedChat: User,
  onUpdateMessages: (newMessages: Message[]) => void
) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentMessages, setCurrentMessages] = useState<Message[]>([]);

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

      const assistantMessageId = Date.now();
      updatedMessages.push({
        id: assistantMessageId,
        name: "Optimism GovGPT",
        message: "",
        timestamp: assistantMessageId,
      });
      setCurrentMessages([...updatedMessages]);
      onUpdateMessages([...updatedMessages]);

      try {
        const reader = await sendMessageApi(newMessage.message);
        const decoder = new TextDecoder();

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

        updatedMessages[updatedMessages.length - 1] = {
          id: Date.now(),
          name: "Optimism GovGPT",
          message: "Sorry, an error occurred while processing your request.",
          timestamp: Date.now(),
        };
        setCurrentMessages([...updatedMessages]);
        onUpdateMessages([...updatedMessages]);
      }
    },
    [currentMessages, onUpdateMessages, sendMessageApi]
  );

  const handleRegenerateMessage = useCallback(
    (messageId: number) => {
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
    [currentMessages, onUpdateMessages, sendMessage]
  );

  return {
    isStreaming,
    inputMessage,
    setInputMessage,
    isTyping,
    currentMessages,
    sendMessage,
    handleRegenerateMessage,
  };
}
