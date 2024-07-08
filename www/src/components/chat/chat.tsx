import type { Message, UserData } from "@/app/data";
import React, { useState, useCallback } from "react";
import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";

interface ChatProps {
  messages?: Message[];
  selectedUser: UserData;
  isMobile: boolean;
}

export function Chat({ messages, selectedUser, isMobile }: ChatProps) {
  const [messagesState, setMessages] = useState<Message[]>(messages ?? []);
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = useCallback(
    async (newMessage: Message) => {
      setMessages((prev) => [...prev, newMessage]);
      setIsStreaming(true);

      try {
        const response = await fetch(
          process.env.NEXT_PUBLIC_CHAT_STREAMING_API_URL!,
          // "http://localhost:9090/predict_stream",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ question: newMessage.message }),
          }
        );

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
          let assistantMessage = "";
          const assistantMessageId = Date.now() + 1;
          setMessages((prev) => [
            ...prev,
            {
              id: assistantMessageId,
              name: selectedUser.name,
              message: "",
              avatar: selectedUser.avatar,
            },
          ]);

          while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            assistantMessage += chunk;
            if (chunk.trim() === "[DONE]") {
              setIsStreaming(false);
              break;
            }
            if (chunk.startsWith("error:")) {
              console.error("Error from server:", chunk.slice(6));
              setIsStreaming(false);
              break;
            }

            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, message: assistantMessage }
                  : msg
              )
            );
          }
        }
      } catch (error) {
        console.error("Error:", error);
        setIsStreaming(false);
      }
    },
    [selectedUser]
  );

  return (
    <div className="flex flex-col justify-between w-full h-full">
      <ChatTopbar selectedUser={selectedUser} />
      <ChatList
        messages={messagesState}
        selectedUser={selectedUser}
        sendMessage={sendMessage}
        isMobile={isMobile}
        isStreaming={isStreaming}
      />
    </div>
  );
}
