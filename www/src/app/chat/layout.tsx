import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type React from "react";

const MOCK_CHAT = [
  "Chat Keyboard K Keyboareyboar Keyboar Chat keboardsewajieawjiewaeioawk",
  "Chat Keyboard  KeyboarChat keboards",
  "Chat Keyboard  Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard K Keyboareyboar Keyboar Chat keboardsewajieawjiewaeioawk",
  "Chat Keyboard  KeyboarChat keboards",
  "Chat Keyboard  Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard K Keyboareyboar Keyboar Chat keboardsewajieawjiewaeioawk",
  "Chat Keyboard  KeyboarChat keboards",
  "Chat Keyboard  Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard K Keyboareyboar Keyboar Chat keboardsewajieawjiewaeioawk",
  "Chat Keyboard  KeyboarChat keboards",
  "Chat Keyboard  Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard  Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
  "Chat Keyboard C Keyboarhat keboards",
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
    <div className="flex max-h-[calc(100dvh-4rem)] overflow-hidden">
      <aside className="w-64 bg-chat-primary flex flex-col h-full">
        <div className="flex items-center justify-between  p-5">
          <h2 className="font-bold text-lg">Chats ({MOCK_CHAT.length})</h2>
          <div className="w-9 h-9 bg-optimism" />
        </div>
        <ScrollArea className="flex-grow px-5">
          <div className="space-y-3 pt-2">
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
        </ScrollArea>
      </aside>
      <main className="flex flex-1 flex-col-reverse">{children}</main>
    </div>
  );
}
