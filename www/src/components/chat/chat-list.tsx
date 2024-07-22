import type { Message } from "@/app/data";
import type { ChatData } from "@/lib/chat-utils";
import { cn } from "@/lib/utils";
import { Clipboard, RotateCcw, ThumbsDown } from "lucide-react";
import { usePostHog } from "posthog-js/react";
import React, { useEffect, useRef, useState } from "react";
import { Avatar, AvatarImage, BoringAvatar } from "../ui/avatar";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { FormattedMessage } from "../ui/formatted-message";
import { useToast } from "../ui/hooks/use-toast";
import { Label } from "../ui/label";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group";
import { Textarea } from "../ui/textarea";

interface ChatListProps {
  messages?: Message[];
  selectedChat: ChatData;
  isMobile: boolean;
  isStreaming: boolean;
  onRegenerateMessage: (messageId: string) => void;
  loadingMessageId: string | null;
}

export function ChatList({
  messages,
  selectedChat,
  isMobile,
  isStreaming,
  onRegenerateMessage,
  loadingMessageId,
}: ChatListProps) {
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<Message | null>(null);
  const [feedbackReason, setFeedbackReason] = useState<string>("");
  const [feedbackDetails, setFeedbackDetails] = useState<string>("");
  const { toast } = useToast();
  const posthog = usePostHog();

  useEffect(() => {
    if (!messagesContainerRef.current) return;

    messagesContainerRef.current.scrollTop =
      messagesContainerRef.current.scrollHeight;
  }, []);

  const deduplicateLineBreaks = (message: string) => {
    return message.replace(/\n{3,}/g, "\n\n");
  };

  const handleNegativeReaction = (message: Message) => {
    posthog.capture("USER_REACTED_NEGATIVELY_TO_MESSAGE", {
      messageId: message.id,
      messages: messages,
    });

    setFeedbackMessage(message);
  };

  const handleFeedbackSubmit = () => {
    posthog.capture("USER_SENT_FEEDBACK", {
      messageId: feedbackMessage?.id,
      messages: messages,
      reason: feedbackReason,
      details: feedbackDetails,
    });

    setFeedbackMessage(null);
    setFeedbackReason("");
    setFeedbackDetails("");
  };

  const handleCopyMessage = (message: string) => {
    navigator.clipboard.writeText(message).then(() => {
      toast({
        title: "Copied to clipboard",
        description: "The message has been copied to your clipboard.",
      });
    });
  };

  return (
    <div
      ref={messagesContainerRef}
      className="w-full overflow-y-auto overflow-x-hidden h-full flex flex-col"
    >
      {messages?.map((message) => (
        <div
          key={message.timestamp}
          className={cn(
            "flex flex-col gap-2 p-4",
            message.name !== "Optimism GovGPT" ? "items-end" : "items-start"
          )}
        >
          <div className="flex gap-3 items-start">
            {message.name === "Optimism GovGPT" && (
              <Avatar className="flex justify-center items-center mt-1">
                <AvatarImage
                  src="/op-logo.png"
                  alt="Optimism GovGPT"
                  width={6}
                  height={6}
                  className="w-10 h-10"
                />
              </Avatar>
            )}
            <div
              className={cn(
                "p-3 rounded-md max-w-md overflow-hidden",
                "bg-accent"
              )}
            >
              {loadingMessageId === message.id ? (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse" />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-75" />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-150" />
                </div>
              ) : (
                <>
                  <FormattedMessage
                    content={deduplicateLineBreaks(message.message)}
                  />
                  {!isStreaming && message.name === "Optimism GovGPT" && (
                    <div className="mt-2 flex gap-3 ">
                      <Button
                        variant="ghost"
                        className="px-0"
                        size="sm"
                        onClick={() => handleCopyMessage(message.message)}
                      >
                        <Clipboard className="h-3.5 w-3.5" />
                      </Button>
                      {/* <Button
                        variant="ghost"
                        className="px-0"
                        size="sm"
                        onClick={() => onRegenerateMessage(message.id)}
                      >
                        <RotateCcw className="h-3.5 w-3.5" />
                      </Button> */}
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            variant="ghost"
                            className="px-0"
                            size="sm"
                            onClick={() => handleNegativeReaction(message)}
                          >
                            <ThumbsDown className="h-3.5 w-3.5" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>
                              What's wrong with this response?
                            </DialogTitle>
                          </DialogHeader>
                          <RadioGroup
                            onValueChange={setFeedbackReason}
                            value={feedbackReason}
                          >
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem
                                value="incomplete"
                                id="incomplete"
                              />
                              <Label htmlFor="incomplete">Incomplete</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem
                                value="inaccurate"
                                id="inaccurate"
                              />
                              <Label htmlFor="inaccurate">Inaccurate</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem
                                value="unrelated"
                                id="unrelated"
                              />
                              <Label htmlFor="unrelated">
                                Not related to the question
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="outdated" id="outdated" />
                              <Label htmlFor="outdated">Outdated</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="other" id="other" />
                              <Label htmlFor="other">Other</Label>
                            </div>
                          </RadioGroup>
                          <Textarea
                            placeholder="Give us some more details..."
                            value={feedbackDetails}
                            onChange={(e) => setFeedbackDetails(e.target.value)}
                          />
                          <DialogClose asChild>
                            <Button onClick={handleFeedbackSubmit}>
                              Submit Feedback
                            </Button>
                          </DialogClose>
                        </DialogContent>
                      </Dialog>
                    </div>
                  )}
                </>
              )}
            </div>
            {message.name !== "Optimism GovGPT" && (
              <Avatar className="flex justify-center items-center mt-1">
                <BoringAvatar name={message.name} />
              </Avatar>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
