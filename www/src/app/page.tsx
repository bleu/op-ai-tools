"use client";
import { Chat } from "@/components/chat/chat";
import Image from "next/image";
import {
	type PartialReablocksTheme,
	ThemeProvider,
	extendTheme,
	theme,
} from "reablocks";

const customTheme: PartialReablocksTheme = {
	components: {
		button: {
			base: "bg-lime-600 text-gray-300",
			variants: {
				filled: "bg-lime-600 hover:bg-lime-700",
				outline: "bg-transparent border-lime-600 border",
				text: "bg-transparent border-0",
			},
			sizes: {
				small: "p-2",
				medium: "p-3",
				large: "p-4",
			},
		},
	},
};
export default function Home() {
	return (
		<main className="flex min-h-screen flex-col items-center justify-between p-24">
			<ThemeProvider theme={extendTheme(theme, customTheme)}>
				<Chat isMobile={false} />
			</ThemeProvider>
		</main>
	);
}
