import { FileText, Vote, HelpCircle, PieChart } from "lucide-react";
import type { Message, User } from "@/app/data";
import React, { useState, useCallback } from "react";
import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";
import { ChatEmptyState } from "./chat-emptystate";
import ChatBottombar from "./chat-bottombar";
import { timeStamp } from "console";

interface ChatProps {
  selectedChat: User;
  messages: Message[];
  isMobile: boolean;
  onUpdateMessages: (newMessages: Message[]) => void;
}

export function Chat({
  selectedChat,
  messages,
  isMobile,
  onUpdateMessages,
}: ChatProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = useCallback(
    async (newMessage: Message) => {
      const updatedMessages = [...messages, newMessage];
      onUpdateMessages(updatedMessages);
      setIsStreaming(true);
      setIsTyping(true);

      // Add a loading message immediately
      const loadingMessageId = Date.now();
      updatedMessages.push({
        id: loadingMessageId,
        name: "Optimism GovGPT",
        message: "Loading...",
        isLoading: true,
        timestamp: loadingMessageId,
      });
      onUpdateMessages([...updatedMessages]);

      try {
        if (!process.env.NEXT_PUBLIC_CHAT_STREAMING_API_URL) return;

        const response = await fetch(
          process.env.NEXT_PUBLIC_CHAT_STREAMING_API_URL,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
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
        onUpdateMessages([...updatedMessages]);
      }
    },
    [messages, onUpdateMessages]
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
      <ChatTopbar isTyping={isTyping} />
      <div className="flex-grow overflow-hidden relative">
        {messages.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <ChatEmptyState suggestions={suggestions} />
          </div>
        ) : (
          <ChatList
            messages={messages}
            selectedUser={selectedChat}
            isMobile={isMobile}
            isStreaming={isStreaming}
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
