import type { Message } from "@/app/data";
import { format, isValid } from "date-fns";

export interface ChatData {
  id: number;
  name: string;
  messages: Message[];
  timestamp: number;
}

export const getChatName = (messages: Message[]): string => {
  const firstQuestion = messages.find((m) => m.name !== "Optimism GovGPT");
  if (firstQuestion) {
    return (
      firstQuestion.message.slice(0, 30) +
      (firstQuestion.message.length > 30 ? "..." : "")
    );
  }
  return "New Chat";
};

export const getValidTimestamp = (timestamp: number | undefined): number => {
  if (timestamp && !Number.isNaN(timestamp)) {
    return timestamp;
  }
  return Date.now();
};

export const saveChatsToLocalStorage = (chats: ChatData[]): void => {
  const nonEmptyChats = chats.filter((chat) => chat.messages.length > 0);
  const chatHistory = nonEmptyChats.reduce(
    (acc, chat) => {
      acc[`chat-${chat.id}`] = chat.messages;
      return acc;
    },
    {} as Record<string, Message[]>,
  );
  localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
};

export const loadChatsFromLocalStorage = (): ChatData[] => {
  const savedHistory = localStorage.getItem("chatHistory");
  if (savedHistory) {
    const parsedHistory = JSON.parse(savedHistory);
    return Object.entries(parsedHistory)
      .map(([name, messages]) => ({
        id: Number.parseInt(name.split("-")[1]),
        name: getChatName(messages as Message[]),
        messages: messages as Message[],
        timestamp: getValidTimestamp((messages as Message[])[0]?.timestamp),
      }))
      .sort((a, b) => b.timestamp - a.timestamp);
  }
  return [];
};

export const addNewChat = (chats: ChatData[]): ChatData[] => {
  const newChat: ChatData = {
    id: Date.now(),
    name: "New Chat",
    messages: [],
    timestamp: Date.now(),
  };
  return [newChat, ...chats];
};

export const formatDate = (timestamp: number) => {
  const date = new Date(timestamp);
  if (isValid(date)) {
    return format(date, "MMM d, yyyy h:mm a");
  }
  return "Invalid date";
};
