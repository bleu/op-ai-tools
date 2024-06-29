import type { Config } from "tailwindcss";
import colors from "tailwindcss/colors";

const config: Config = {
	content: [
		"./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/components/**/*.{js,ts,jsx,tsx,mdx}",
		"./src/app/**/*.{js,ts,jsx,tsx,mdx}",
		"node_modules/reablocks/**/*.js",
	],
	theme: {
		extend: {
			colors: {
				primary: {
					50: "#f3f4f6",
					100: "#e7e9ed",
					200: "#c3c8d3",
					300: "#9fa6b9",
					400: "#565f86",
					500: "#0d1733",
					600: "#0c1530",
					700: "#0a1228",
					800: "#080f20",
					900: "#060c19",
				},
				secondary: colors.slate,
			},
			backgroundImage: {
				"gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
				"gradient-conic":
					"conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
			},
		},
	},
	plugins: [],
};
export default config;
