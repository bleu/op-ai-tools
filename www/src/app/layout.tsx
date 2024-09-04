import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/Header";
import { CSPostHogProvider } from "@/components/posthog";
import { Toaster } from "@/components/ui/toaster";
import { cn } from "@/lib/utils";
import dynamic from "next/dynamic";
import { Roboto_Flex } from "next/font/google";

const PostHogPageView = dynamic(() => import("@/components/posthog-pageview"), {
  ssr: false,
});

const robotoFlex = Roboto_Flex({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Optimism GovGPT",
  description: "Ask me anything about Optimism Governance!",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: 1,
};

if (process.env.NEXT_PUBLIC_API_MOCKING === "enabled") {
  require("../mocks");
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={robotoFlex.className}>
      <head>
        {/* TODO OP-67: fix - this is requesting the route for a logo <link rel="icon" href="op-logo.svg" type="image/x-icon" /> */}
      </head>
      <CSPostHogProvider>
        <body className="flex flex-col min-h-screen text-primary">
          <Header />
          <div className="flex flex-1">
            <PostHogPageView />
            <Toaster />
            {children}
          </div>
        </body>
      </CSPostHogProvider>
    </html>
  );
}
