import type React from "react";
import { useState } from "react";

import { Pencil } from "lucide-react";

import type { Message as MessageType } from "@/app/data";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { MessageAvatar } from "./message-avatar";
import { MessageContent } from "./message-content";

export interface MessageProps {
	message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
	const [isEditable, setIsEditable] = useState(false);
	const [isHovered, setIsHovered] = useState(false);

	const handleEditClick = () => {
		setIsEditable(true);
	};

	const isAnswer = message.name === "Optimism GovGPT";

	return (
		<div
			className={cn(
				"flex flex-col gap-2 p-4",
				isAnswer ? "items-start" : "items-end",
			)}
			onMouseEnter={() => setIsHovered(true)}
			onMouseLeave={() => setIsHovered(false)}
		>
			<div
				className={cn(
					"flex gap-3 items-start",
					isAnswer ? "flex-row" : "flex-row-reverse",
				)}
			>
				<MessageAvatar name={message.name} />
				<div className="flex flex-col">
					<MessageContent
						message={message}
						isEditable={isEditable}
						setIsEditable={setIsEditable}
						isHovered={isHovered}
					/>
				</div>
				{!isAnswer && isHovered && (
					<Button
						variant="ghost"
						className="px-0 mt-1"
						size="sm"
						onClick={handleEditClick}
					>
						<Pencil className="h-3.5 w-3.5" />
					</Button>
				)}
			</div>
		</div>
	);
};
