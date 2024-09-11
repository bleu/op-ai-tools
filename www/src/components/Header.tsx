"use client";

import Image from "next/image";
import Link from "next/link";
import { MobileSidebar } from "./forum/Sidebar";

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
          <span className="text-xs md:text-sm font-medium">GovSummarizer</span>
        </Link>
      </div>
    </header>
  );
}
