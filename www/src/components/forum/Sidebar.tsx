"use client";

import React from "react";
import Link from "next/link";
import { BarChart2, Clock, Menu, ExternalLink, LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Octagram } from "./Octagram";
import { CATEGORY_COLORS } from "./categoryColors";

interface NavSection {
  title: string;
  items: NavItem[];
}

interface NavItem {
  href: string;
  icon: LucideIcon | typeof Octagram;
  label: string;
  className?: string;
}

interface NavLinkProps extends NavItem {
  isMobile: boolean;
  isSelected: boolean;
  isCategory?: boolean;
}

interface NavContentProps {
  isMobile: boolean;
}

const navSections: NavSection[] = [
  {
    title: "Feeds",
    items: [
      {
        href: "/forum/trending-topics",
        icon: BarChart2,
        label: "Trending topics",
        className: "bg-gray-100",
      },
      {
        href: "/forum/latest-topics",
        icon: Clock,
        label: "Latest topics",
        className: "bg-gray-100",
      },
    ],
  },
  {
    title: "Categories",
    items: [
      {
        href: "#",
        icon: Octagram,
        label: "All",
        className: CATEGORY_COLORS["All"],
      },
      {
        href: "#",
        icon: Octagram,
        label: "Delegates",
        className: CATEGORY_COLORS["Delegates"],
      },
      {
        href: "#",
        icon: Octagram,
        label: "General Discussions",
        className: CATEGORY_COLORS["General Discussions"],
      },
      {
        href: "#",
        icon: Octagram,
        label: "Mission Grants",
        className: CATEGORY_COLORS["Mission Grants"],
      },
      {
        href: "#",
        icon: Octagram,
        label: "Updates and Announcements",
        className: CATEGORY_COLORS["Updates and Announcements"],
      },
      {
        href: "#",
        icon: Octagram,
        label: "Retro Funding",
        className: CATEGORY_COLORS["Retro Funding"],
      },
      {
        href: "#",
        icon: Octagram,
        label: "Others",
        className: CATEGORY_COLORS["Others"],
      },
    ],
  },
];

function NavLink({
  href,
  icon: Icon,
  label,
  className,
  isMobile,
  isSelected,
  isCategory,
}: NavLinkProps) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-1.5 transition-all text-sm",
        !isCategory && className,
        isSelected
          ? "bg-[#FFDBDF] text-optimism font-semibold"
          : "hover:bg-gray-100"
      )}
    >
      <Icon
        className={cn(
          isMobile ? "h-5 w-5" : "h-4 w-4",
          isCategory && className
        )}
        label={label}
      />
      <span>{label}</span>
    </Link>
  );
}

function NavContent({ isMobile }: NavContentProps) {
  const pathname = usePathname();
  return (
    <div className={cn("flex flex-col gap-y-2", isMobile && "py-2")}>
      {navSections.map((section, index) => (
        <React.Fragment key={index}>
          {index > 0 && <hr className="border-t border-gray-200 my-4" />}
          <div>
            <h2
              className={cn(
                "mb-2 px-3 font-semibold",
                isMobile ? "text-xl" : "text-lg"
              )}
            >
              {section.title}
            </h2>
            <nav className="grid gap-y-3">
              {section.items.map((item, itemIndex) => (
                <NavLink
                  key={itemIndex}
                  {...item}
                  isMobile={isMobile}
                  isSelected={pathname === item.href}
                  isCategory={section.title === "Categories"}
                />
              ))}
            </nav>
          </div>
        </React.Fragment>
      ))}
      <hr className="border-t border-gray-200 my-4" />
      <div>
        <h2
          className={cn(
            "mb-2 px-3 font-semibold",
            isMobile ? "text-xl" : "text-lg"
          )}
        >
          Have any questions?
        </h2>
        <Link
          href="/"
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:bg-gray-100 text-gray-700 text-sm"
          )}
        >
          Ask GovGPT{" "}
          <ExternalLink className={cn(isMobile ? "h-5 w-5" : "h-4 w-4")} />
        </Link>
      </div>
    </div>
  );
}

export function DesktopSidebar() {
  return (
    <div className="hidden border-r bg-white md:block h-full w-full">
      <div className="flex h-full max-h-screen flex-col gap-2 p-4">
        <NavContent isMobile={false} />
      </div>
    </div>
  );
}

export function MobileSidebar() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="shrink-0 md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle navigation menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="flex flex-col w-[280px] p-0">
        <div className="overflow-y-auto px-4 py-6">
          <NavContent isMobile={true} />
        </div>
      </SheetContent>
    </Sheet>
  );
}
