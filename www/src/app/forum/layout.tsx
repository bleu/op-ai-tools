import { Header } from "@/components/Header";
import { DesktopSidebar } from "@/components/forum/Sidebar";
import type { PropsWithChildren } from "react";

export default function Layout({ children }: PropsWithChildren<{}>) {
  return (
    <div className="flex-1">
      <Header />
      <div className="grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr]">
        <div className="hidden md:block">
          <DesktopSidebar />
        </div>
        <div className="flex flex-col">
          <main className="flex flex-1 flex-col gap-4 py-4 lg:gap-6 lg:py-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
