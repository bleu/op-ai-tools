import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Menu } from "lucide-react";
import type React from "react";
import { useState } from "react";
import { Button } from "../ui/button";
import ChatSidebar from "./chat-sidebar";

export const ChatMobileSidebar: React.FC = () => {
  const [open, setOpen] = useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="shrink-0 md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle navigation menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="flex flex-col w-64 p-0">
        <ChatSidebar />
      </SheetContent>
    </Sheet>
  );
};
