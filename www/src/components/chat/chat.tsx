import type { Message, User } from "@/app/data";
import { FileText, HelpCircle, PieChart, Vote } from "lucide-react";
import React, { useState, useCallback, useEffect } from "react";
import { usePostHog } from "posthog-js/react";
import ChatBottombar from "./chat-bottombar";
import { ChatEmptyState } from "./chat-emptystate";
import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";

interface ChatProps {
  selectedChat: User;
  isMobile: boolean;
  onUpdateMessages: (newMessages: Message[]) => void;
  onToggleSidebar: () => void;
}

export function Chat({
  selectedChat,
  isMobile,
  onUpdateMessages,
  onToggleSidebar,
}: ChatProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentMessages, setCurrentMessages] = useState<Message[]>([]);
  const posthog = usePostHog();

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

      const loadingMessageId = Date.now();
      updatedMessages.push({
        id: loadingMessageId,
        name: "Optimism GovGPT",
        message: "Loading...",
        isLoading: true,
        timestamp: loadingMessageId,
      });
      setCurrentMessages([...updatedMessages]);
      onUpdateMessages([...updatedMessages]);

      try {
        if (!process.env.NEXT_PUBLIC_CHAT_STREAMING_API_URL) return;

        const response = await fetch(
          process.env.NEXT_PUBLIC_CHAT_STREAMING_API_URL,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-User-ID": posthog.get_distinct_id(),
            },
            body: JSON.stringify({ question: newMessage.message }),
          }
        );

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
          let assistantMessage = "";
          const assistantMessageId = Date.now() + 1;

          updatedMessages[updatedMessages.length - 1] = {
            id: assistantMessageId,
            name: "Optimism GovGPT",
            message: "",
            timestamp: Date.now(),
          };

          while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            assistantMessage += chunk;
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

            updatedMessages[updatedMessages.length - 1].message =
              assistantMessage;
            setCurrentMessages([...updatedMessages]);
            onUpdateMessages([...updatedMessages]);
          }
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
    [currentMessages, onUpdateMessages, posthog]
  );

  const handleRegenerateMessage = useCallback(
    (messageId: number) => {
      const messageIndex = currentMessages.findIndex((m) => m.id === messageId);
      if (messageIndex === -1) return;

      // Remove all messages after the selected message
      const updatedMessages = currentMessages.slice(0, messageIndex);
      setCurrentMessages(updatedMessages);
      onUpdateMessages(updatedMessages);

      // Resend the user message that preceded the AI message
      const userMessage = currentMessages[messageIndex - 1];
      if (userMessage) {
        sendMessage(userMessage);
      }
    },
    [currentMessages, onUpdateMessages, sendMessage]
  );

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  const suggestions = [
    {
      icon: <FileText size={20} />,
      text: "Explain recent proposal",
      onClick: () =>
        handleSuggestionClick(
          "Can you explain the most recent Optimism governance proposal?"
        ),
    },
    {
      icon: <Vote size={20} />,
      text: "How to vote",
      onClick: () =>
        handleSuggestionClick(
          "How can I participate in voting on Optimism governance proposals?"
        ),
    },
    {
      icon: <PieChart size={20} />,
      text: "OP token distribution",
      onClick: () =>
        handleSuggestionClick(
          "Can you give me an overview of the OP token distribution?"
        ),
    },
    {
      icon: <HelpCircle size={20} />,
      text: "Optimism Collective",
      onClick: () =>
        handleSuggestionClick(
          "What is the Optimism Collective and how does it work?"
        ),
    },
  ];

  return (
    <div className="flex flex-col w-full h-full">
      <ChatTopbar
        isTyping={isTyping}
        onToggleSidebar={onToggleSidebar}
        isMobile={isMobile}
      />
      <div className="flex-grow overflow-hidden relative">
        {selectedChat.messages.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <ChatEmptyState suggestions={suggestions} />
          </div>
        ) : (
          <ChatList
            messages={selectedChat.messages}
            selectedUser={selectedChat}
            isMobile={isMobile}
            isStreaming={isStreaming}
            onRegenerateMessage={handleRegenerateMessage}
          />
        )}
      </div>
      <ChatBottombar
        sendMessage={sendMessage}
        isMobile={isMobile}
        isStreaming={isStreaming}
        inputMessage={inputMessage}
        setInputMessage={setInputMessage}
      />
    </div>
  );
}
