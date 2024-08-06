import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";
import Image from "next/image";
import Link from "next/link";
import { MobileSidebar } from "./Sidebar";

export function Header() {
  return (
    <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-4 lg:h-[60px] lg:px-6">
      <div className="md:hidden">
        <MobileSidebar />
      </div>
      <div className="w-full flex-1 flex justify-between items-center">
        <Link
          href="/forum/latest-topics"
          className="flex flex-col gap-x-3 md:flex-row"
        >
          <Image
            src="/optimism.svg"
            alt="logo"
            width={100}
            height={100}
            className="w-[100px] md:w-[150px]"
          />
          <span className="text-xs md:text-sm font-light">GovSummarizer</span>
        </Link>
        {/* <form className="w-1/2 hidden md:block">
          <div className="relative">
            <Search className="absolute right-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              className="w-full appearance-none bg-background pr-8 shadow-none rounded-2xl focus-visible:ring-"
            />
          </div>
        </form> */}
      </div>
    </header>
  );
}
