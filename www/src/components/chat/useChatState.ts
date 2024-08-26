import { create } from "zustand";

import type { Message } from "@/app/data";
import { type ChatData, generateMessageParams } from "@/lib/chat-utils";
import React, { useEffect } from "react";
import { useChatApi } from "./useChatApi";

interface ChatState {
  selectedChat: ChatData | null;
  currentMessages: Message[];
  isStreaming: boolean;
  isTyping: boolean;
  loadingMessageId: string | null;
  inputMessage: string;
  setSelectedChat: (chat: ChatData) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setIsTyping: (isTyping: boolean) => void;
  setLoadingMessageId: (id: string | null) => void;
  setInputMessage: (message: string) => void;
  editMessage: (messageId: string, newMessage: Message) => void;
}

const useChatStore = create<ChatState>((set) => ({
  selectedChat: null,
  currentMessages: [],
  isStreaming: false,
  isTyping: false,
  loadingMessageId: null,
  inputMessage: "",
  setSelectedChat: (chat) => {
    console.log("Setting selected chat", chat);
    set({ selectedChat: chat, currentMessages: chat.messages || [] });
  },
  addMessage: (message) =>
    set((state) => ({ currentMessages: [...state.currentMessages, message] })),
  updateLastMessage: (content) =>
    set((state) => {
      const updatedMessages = [...state.currentMessages];
      const lastIndex = updatedMessages.length - 1;
      if (lastIndex >= 0) {
        updatedMessages[lastIndex] = {
          ...updatedMessages[lastIndex],
          message: content,
        };
      }
      return { currentMessages: updatedMessages };
    }),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  setIsTyping: (isTyping) => set({ isTyping }),
  setLoadingMessageId: (id) => set({ loadingMessageId: id }),
  setInputMessage: (message) => set({ inputMessage: message }),
  editMessage: (messageId, newMessage) =>
    set((state) => {
      const messageIndex = state.currentMessages.findIndex(
        (m) => m.id === messageId,
      );
      if (messageIndex === -1) return state;
      const updatedMessages = state.currentMessages.slice(0, messageIndex);
      return { currentMessages: updatedMessages };
    }),
}));

export function useChatState() {
  const { sendMessage: sendMessageApi } = useChatApi();
  const {
    currentMessages,
    isStreaming,
    isTyping,
    loadingMessageId,
    inputMessage,
    selectedChat,
    addMessage,
    updateLastMessage,
    setIsStreaming,
    setIsTyping,
    setLoadingMessageId,
    setInputMessage,
    editMessage,
  } = useChatStore();

  const createAssistantMessage = () => {
    return generateMessageParams(selectedChat?.id || "", "", "Optimism GovGPT");
  };

  const handleApiResponse = (response: any) => {
    const content = Array.isArray(response.answer)
      ? response.answer.join("\n")
      : response.answer;
    updateLastMessage(content);
  };

  const handleApiError = () => {
    const errorMessage =
      "Sorry, an error occurred while processing your request.";
    updateLastMessage(errorMessage);
  };

  const resetChatState = () => {
    setIsStreaming(false);
    setIsTyping(false);
    setLoadingMessageId(null);
  };

  const sendMessage = async (newMessage: Message) => {
    addMessage(newMessage);
    setIsStreaming(true);
    setIsTyping(true);

    const assistantMessage = createAssistantMessage();
    setLoadingMessageId(assistantMessage.id);
    addMessage(assistantMessage);

    try {
      const response = await sendMessageApi(
        newMessage.message,
        currentMessages,
      );
      handleApiResponse(response);
    } catch (error) {
      console.error("Error:", error);
      handleApiError();
    } finally {
      resetChatState();
    }
  };

  const handleOnEditMessage = (messageId: string, newMessage: Message) => {
    editMessage(messageId, newMessage);
    sendMessage(newMessage);
  };

  return {
    isStreaming,
    inputMessage,
    setInputMessage,
    isTyping,
    currentMessages,
    sendMessage,
    handleOnEditMessage,
    loadingMessageId,
  };
}

export { useChatStore };
