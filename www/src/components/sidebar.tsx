import type { Message } from "@/app/data";
import { buttonVariants } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { getChatName } from "@/lib/chat-utils";
import { formatDate } from "@/lib/chat-utils";
import { cn } from "@/lib/utils";
import { MoreHorizontal, SquarePen } from "lucide-react";
import Link from "next/link";
import { Avatar, AvatarImage } from "./ui/avatar";
import { ScrollArea } from "./ui/scroll-area";

interface SidebarProps {
  isCollapsed: boolean;
  links: {
    id: string;
    name: string;
    messages: Message[];
    variant: "grey" | "ghost" | "default";
    timestamp: number;
  }[];
  onClick?: () => void;
  isMobile: boolean;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
}

export function Sidebar({
  links,
  isCollapsed,
  isMobile,
  onSelectChat,
  onNewChat,
}: SidebarProps) {
  return (
    <div
      data-collapsed={isCollapsed}
      className="relative group flex flex-col h-full gap-4 p-2 data-[collapsed=true]:p-2 "
    >
      {!isCollapsed && (
        <div className="flex justify-between p-2 items-center">
          <div className="flex gap-2 items-center text-2xl">
            <p className="font-medium">Chats</p>
            <span className="text-zinc-300">({links.length})</span>
          </div>

          <div>
            <Link
              href="#"
              className={cn(
                buttonVariants({ variant: "ghost", size: "icon" }),
                "h-9 w-9",
              )}
              onClick={onNewChat}
            >
              <SquarePen size={20} />
            </Link>
          </div>
        </div>
      )}
      <ScrollArea className="flex-1">
        <nav className="grid gap-1 px-2 group-[[data-collapsed=true]]:justify-center group-[[data-collapsed=true]]:px-2">
          {links.map((link, index) =>
            isCollapsed ? (
              <TooltipProvider key={link.timestamp}>
                <Tooltip key={link.timestamp} delayDuration={0}>
                  <TooltipTrigger asChild>
                    <Link
                      href="#"
                      onClick={() => onSelectChat(link.id)}
                      className={cn(
                        buttonVariants({ variant: link.variant, size: "icon" }),
                        "h-11 w-11 md:h-16 md:w-16",
                        link.variant === "grey" &&
                          "dark:bg-muted dark:text-muted-foreground dark:hover:bg-muted dark:hover:text-white",
                      )}
                    >
                      <span className="sr-only">{link.name}</span>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent
                    side="right"
                    className="flex items-center gap-4"
                  >
                    {link.name}
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            ) : (
              <Link
                key={link.timestamp}
                href="#"
                onClick={() => onSelectChat(link.id)}
                className={cn(
                  buttonVariants({ variant: link.variant, size: "xl" }),
                  link.variant === "grey" &&
                    "dark:bg-muted dark:text-white dark:hover:bg-muted dark:hover:text-white shrink",
                  "justify-start gap-4",
                )}
              >
                <div className="flex flex-col max-w-28">
                  <span>{getChatName(link.messages)}</span>
                  <span className="text-zinc-300 text-xs">
                    {formatDate(link.timestamp)}
                  </span>
                </div>
              </Link>
            ),
          )}
        </nav>
      </ScrollArea>
    </div>
  );
}
