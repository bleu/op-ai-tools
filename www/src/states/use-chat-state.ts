import type { Message } from "@/app/data";
import type { StoreApi, UseBoundStore } from "zustand";
import { persist } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";
import { sendMessage as sendMessageApi } from "../components/chat/send-message";

import {
  type ChatData,
  generateChatParams,
  generateMessageParams,
  generateMessagesMemory,
  getChatName,
} from "@/lib/chat-utils";
import { create } from "zustand";

interface ChatStoreState {
  chats: Record<string, ChatData>;
  selectedChatId: string | null;
  isStreaming: boolean;
  isTyping: boolean;
  loadingMessageId: string | null;
  inputMessage: string;
}

interface ChatStoreActions {
  setSelectedChatId: (chatId: string) => void;
  addChat: () => void;
  removeChat: (id: string) => void;
  addMessage: (chatId: string, message: Message) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setIsTyping: (isTyping: boolean) => void;
  setLoadingMessageId: (id: string | null) => void;
  setInputMessage: (
    message: string | ((prevMessage: string) => string),
  ) => void;
  sendMessage: (newMessage: Message) => Promise<void>;
}

type ChatStore = ChatStoreState & ChatStoreActions;

type WithSelectors<S> = S extends { getState: () => infer T }
  ? S & { use: { [K in keyof T]: () => T[K] } }
  : never;

const createSelectors = <S extends UseBoundStore<StoreApi<object>>>(
  _store: S,
) => {
  const store = _store as WithSelectors<typeof _store>;
  store.use = {};
  for (const k of Object.keys(store.getState())) {
    (store.use as any)[k] = () => store((s) => s[k as keyof typeof s]);
  }

  return store;
};

const createAssistantMessage = (chatId: string): Message => {
  return generateMessageParams(
    chatId,
    { answer: "", url_supporting: [] },
    "Optimism GovGPT",
  );
};

const useChatStoreBase = create<ChatStore>()(
  persist(
    immer((set, get) => ({
      chats: {},
      selectedChatId: null,
      isStreaming: false,
      isTyping: false,
      loadingMessageId: null,
      inputMessage: "",

      setSelectedChatId: (chatId) => set({ selectedChatId: chatId }),

      addChat: () => {
        const newChat = generateChatParams("chat");
        set((state) => {
          state.chats[newChat.id] = newChat;
          state.selectedChatId = newChat.id;
        });
      },

      removeChat: (id) =>
        set((state) => {
          delete state.chats[id];
        }),

      addMessage: (chatId, message) =>
        set((state) => {
          const chat = state.chats[chatId];
          if (chat) {
            chat.messages.push(message);
            chat.name = getChatName(chat.messages);
          }
        }),

      setIsStreaming: (isStreaming) => set({ isStreaming }),
      setIsTyping: (isTyping) => set({ isTyping }),
      setLoadingMessageId: (id) => set({ loadingMessageId: id }),
      setInputMessage: (message) =>
        set((state) => {
          state.inputMessage =
            typeof message === "function"
              ? message(state.inputMessage)
              : message;
        }),

      sendMessage: async (newMessage: Message) => {
        const state = get();
        const chatId = state.selectedChatId;
        if (!chatId) return;

        const isEditing = state.chats[chatId].messages.some(
          (message) => message.id === newMessage.id,
        );

        set((state) => {
          state.isStreaming = true;
          state.isTyping = true;
          if (isEditing) {
            const messageIndex = state.chats[chatId].messages.findIndex(
              (m) => m.id === newMessage.id,
            );
            if (messageIndex !== -1) {
              state.chats[chatId].messages[messageIndex] = newMessage;
              state.chats[chatId].messages = state.chats[chatId].messages.slice(
                0,
                messageIndex + 1,
              );
            }
          } else {
            state.chats[chatId].messages.push(newMessage);
          }
          state.chats[chatId].name = getChatName(state.chats[chatId].messages);
        });

        try {
          const assistantMessage = createAssistantMessage(chatId);
          set((state) => {
            state.loadingMessageId = assistantMessage.id;
            state.chats[chatId].messages.push(assistantMessage);
          });

          const response = await sendMessageApi(
            newMessage.data.answer,
            generateMessagesMemory(state.chats[chatId].messages),
          );

          set((state) => {
            const lastMessage =
              state.chats[chatId].messages[
                state.chats[chatId].messages.length - 1
              ];
            if (lastMessage.id === assistantMessage.id) {
              lastMessage.data = response.data;
            }
            state.chats[chatId].name = getChatName(
              state.chats[chatId].messages,
            );
          });
        } catch (error) {
          console.error("Error:", error);
          set((state) => {
            const lastMessage =
              state.chats[chatId].messages[
                state.chats[chatId].messages.length - 1
              ];
            if (lastMessage.id === state.loadingMessageId) {
              lastMessage.data.answer =
                "Sorry, an error occurred while processing your request.";
            }
          });
        } finally {
          set((state) => {
            state.isStreaming = false;
            state.isTyping = false;
            state.loadingMessageId = null;
          });
        }
      },
    })),
    {
      name: "chat-storage",
      getStorage: () => localStorage,
    },
  ),
);

export const useChatStore = createSelectors(useChatStoreBase);

export const getCurrentChat = () => {
  const selectedChatId = useChatStore.use.selectedChatId();
  const chats = useChatStore.use.chats();
  return selectedChatId ? chats[selectedChatId] : null;
};
