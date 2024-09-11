import type React from "react";

import { Avatar, AvatarImage, BoringAvatar } from "@/components/ui/avatar";

export interface MessageAvatarProps {
  name: string;
}

export const MessageAvatar: React.FC<MessageAvatarProps> = ({ name }) => {
  if (name === "Optimism GovGPT") {
    return (
      <Avatar className="flex justify-center items-center mt-1">
        <AvatarImage
          src="/op-logo.png"
          alt="Optimism GovGPT"
          width={6}
          height={6}
          className="w-10 h-10"
        />
      </Avatar>
    );
  }
  return (
    <Avatar className="flex justify-center items-center mt-1">
      <BoringAvatar name={name} />
    </Avatar>
  );
};
