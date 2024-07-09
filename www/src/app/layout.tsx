import { GeistSans } from "geist/font/sans";
import type { Metadata } from "next";
import "./globals.css";
import { CSPostHogProvider } from "@/components/posthog";
import dynamic from "next/dynamic";

const PostHogPageView = dynamic(() => import("@/components/posthog-pageview"), {
  ssr: false,
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
    <html lang="en">
      <head>
        <link rel="icon" href="op-logo.svg" type="image/x-icon" />
      </head>
      <CSPostHogProvider>
        <body className={GeistSans.className}>
          <PostHogPageView />
          {children}
        </body>
      </CSPostHogProvider>
    </html>
  );
}
