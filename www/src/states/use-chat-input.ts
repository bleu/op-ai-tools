import React, { useState } from "react";
import { create } from "zustand";

interface ChatInputRefStoreState {
  internalRef: React.MutableRefObject<HTMLTextAreaElement | null>;
}

interface ChatInputRefStoreActions {
  setRef: (ref: React.MutableRefObject<HTMLTextAreaElement | null>) => void;
}

export const useChatInputRefStore = create<
  ChatInputRefStoreState & ChatInputRefStoreActions
>((set) => ({
  internalRef: React.createRef(),
  setRef: (ref: React.MutableRefObject<HTMLTextAreaElement | null>) =>
    set({ internalRef: ref }),
}));
