import { Button } from "@/components/ui/button";
import type React from "react";

const MOCK_CHAT = [
  "Chat Keyboard K Keyboareyboar Keyboar Chat keboardsewajieawjiewaeioawk",
  "Chat Keyboard  KeyboarChat keboards",
  "Chat Keyboard  Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
];

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-1">
      <aside className="w-64 bg-chat-primary p-5">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg">Chats (5)</h2>
          <div className="w-9 h-9 bg-optimism" />
        </div>
        <div className="mt-8 space-y-3">
          {MOCK_CHAT.map((text, index) => (
            <Button
              variant="ghost"
              className={`max-w-full overflow-hidden justify-start px-2 py-0 font-medium text-chat-secondary hover:text-optimism  ${index === 0 && "text-optimism bg-optimism/15 hover:bg-optimism/15"}`}
              key={index}
            >
              {text}
            </Button>
          ))}
        </div>
      </aside>
      <main className="flex flex-1 flex-col-reverse">{children}</main>
    </div>
  );
}
