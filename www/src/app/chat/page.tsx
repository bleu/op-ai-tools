import { MessageActions } from "@/components/chat/message/message-actions";
import { MessageAvatar } from "@/components/chat/message/message-avatar";
import { Button } from "@/components/ui/button";
import { CopyCheck, ThumbsDown } from "lucide-react";
import React from "react";

export default function Chat() {
  return (
    <div className="px-32">
      <div className="flex flex-row gap-3 justify-end mb-8">
        <div
          style={{ maxWidth: "66%" }}
          className="gap-5 bg-chat-primary rounded-lg"
        >
          <p className="p-4">
            Yes, the length of the challenge period can be changed. Currently,
            it is set to keoawkeowak days on the OP Mainnet for a balance
            between security and usab
          </p>
        </div>
      </div>
      <div className="flex flex-row gap-3">
        <MessageAvatar name="ronaldo" />
        <div className="gap-5">
          <p className="mb-4">
            Yes, the length of the challenge period can be changed. Currently,
            it is set to seven days on the OP Mainnet for a balance between
            security and usab
          </p>
          <Button size="icon" variant="ghost" className="hover:bg-chat-primary">
            <CopyCheck />
          </Button>
          <Button size="icon" variant="ghost" className="hover:bg-chat-primary">
            <ThumbsDown />
          </Button>
        </div>
      </div>
    </div>
  );

  //   <div
  //   className={cn(
  //     "flex flex-col gap-2 p-4",
  //     isAnswer ? "items-start" : "items-end",
  //   )}
  //   onMouseEnter={() => setIsHovered(true)}
  //   onMouseLeave={() => setIsHovered(false)}
  // >
  //   <div
  //     className={cn(
  //       "flex gap-3 items-start",
  //       isAnswer ? "flex-row" : "flex-row-reverse",
  //     )}
  //   >
  //     <MessageAvatar name={message.name} />
  //     <div className="flex flex-col">
  //       <MessageContent
  //         message={message}
  //         isEditable={isEditable}
  //         setIsEditable={setIsEditable}
  //         isHovered={isHovered}
  //       />
  //     </div>
  //     {!isAnswer && isHovered && (
  //       <Button
  //         variant="ghost"
  //         className="px-0 mt-1"
  //         size="sm"
  //         onClick={handleEditClick}
  //       >
  //         <Pencil className="h-3.5 w-3.5" />
  //       </Button>
  //     )}
  //   </div>
  // </div>
}
