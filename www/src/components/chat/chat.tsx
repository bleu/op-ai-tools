import { ChatList } from "./chat-list";
import ChatTopbar from "./chat-topbar";

import React from "react";

export const userData = [
	{
		id: 1,
		avatar: "/op-logo.png",
		name: "Optimism Governance GPT",
	},
];

export type UserData = (typeof userData)[number];

export const loggedInUserData = {
	id: 5,
	avatar: "/LoggedInUser.jpg",
	name: "Jakob Hoeg",
};

export type LoggedInUserData = typeof loggedInUserData;

export interface Message {
	id: number;
	avatar: string;
	name: string;
	message: string;
}

export interface User {
	id: number;
	avatar: string;
	messages: Message[];
	name: string;
}

interface ChatProps {
	isMobile: boolean;
}

export function Chat({ isMobile }: ChatProps) {
	const [selectedUser, setSelectedUser] = React.useState(userData[0]);
	const [messagesState, setMessages] = React.useState<Message[]>(
		selectedUser?.messages || [],
	);

	const sendMessage = (newMessage: Message) => {
		setMessages([...messagesState, newMessage]);
	};

	return (
		<div className="flex flex-col justify-between w-full h-full">
			<ChatTopbar selectedUser={selectedUser} />

			<ChatList
				messages={messagesState}
				selectedUser={selectedUser}
				sendMessage={sendMessage}
				isMobile={isMobile}
			/>
		</div>
	);
}
