import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { PlusCircle } from "lucide-react";

interface SidebarProps {
  isCollapsed: boolean;
  links: {
    id: number;
    name: string;
    timestamp: number;
    variant: "default" | "ghost";
  }[];
  onSelectChat: (id: number) => void;
  onNewChat: () => void;
}

export function Sidebar({
  isCollapsed,
  links,
  onSelectChat,
  onNewChat,
}: SidebarProps) {
  return (
    <div
      data-collapsed={isCollapsed}
      className="relative group flex flex-col h-full data-[collapsed=true]:p-2"
    >
      <div className="p-2">
        <Button
          variant="outline"
          className={cn(
            "w-full justify-start",
            isCollapsed && "h-10 w-10 p-0 justify-center",
          )}
          onClick={onNewChat}
        >
          <PlusCircle className="h-4 w-4" />
          {!isCollapsed && <span className="ml-2">New Chat</span>}
        </Button>
      </div>
      <ScrollArea className="flex-1 w-full">
        {links.map((link) => (
          <Button
            key={link.id}
            variant={link.variant}
            className={cn(
              "w-full justify-start",
              isCollapsed
                ? "h-10 w-10 p-0 justify-center"
                : "flex-col items-start h-auto py-2",
            )}
            onClick={() => onSelectChat(link.id)}
          >
            {!isCollapsed && (
              <>
                <span className="text-sm font-medium truncate w-full text-left">
                  {link.name}
                </span>
                {link?.timestamp && (
                  <span className="text-xs text-muted-foreground truncate w-full text-left">
                    {format(link.timestamp, "MMM d, yyyy h:mm a")}
                  </span>
                )}
              </>
            )}
            {isCollapsed && (
              <span className="truncate">{link.name.charAt(0)}</span>
            )}
          </Button>
        ))}
      </ScrollArea>
    </div>
  );
}
