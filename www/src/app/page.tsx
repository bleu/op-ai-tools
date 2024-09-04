import { ChatLayout } from "@/components/chat/chat-layout";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { GitHubLogoIcon } from "@radix-ui/react-icons";
import Link from "next/link";

export default function Home() {
  return (
    <main className="flex h-[calc(100dvh-4rem)] flex-col items-center justify-center p-4 md:px-24 py-32 gap-4">
      <div className="flex max-w-5xl w-full">
        <Link
          href="https://github.com/bleu/op-ai-tools"
          className={cn(
            buttonVariants({ variant: "ghost", size: "icon" }),
            "h-8 w-8 ml-auto",
          )}
        >
          <GitHubLogoIcon className="w-7 h-7 text-muted-foreground" />
        </Link>
      </div>
      <div className="z-10 border rounded-lg max-w-5xl w-full h-full text-sm lg:flex bg-white">
        <ChatLayout />
      </div>

      <div className="flex justify-between max-w-5xl w-full items-start text-xs md:text-sm text-muted-foreground " />
    </main>
  );
}
