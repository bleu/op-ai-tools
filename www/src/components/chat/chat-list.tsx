import type { Data, Message } from "@/app/data";
import { formatAnswerWithReferences } from "@/lib/chat-utils";
import { cn } from "@/lib/utils";
import { Clipboard, Pencil, ThumbsDown } from "lucide-react";
import { usePostHog } from "posthog-js/react";
import React, {
  useCallback,
  useEffect,
  useRef,
  useState,
  useMemo,
} from "react";
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
import { ScrollArea } from "../ui/scroll-area";
import { Textarea } from "../ui/textarea";
import { getCurrentChat, useChatStore } from "./use-chat-state";

export const ChatList: React.FC = React.memo(() => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<Message | null>(null);
  const [feedbackReason, setFeedbackReason] = useState<string>("");
  const [feedbackDetails, setFeedbackDetails] = useState<string>("");
  const [isEditable, setIsEditable] = useState<string>("");
  const [editMessageContent, setEditMessageContent] = useState<string>("");

  const isStreaming = useChatStore.use.isStreaming();
  const loadingMessageId = useChatStore.use.loadingMessageId();
  const sendMessage = useChatStore.use.sendMessage();
  const selectedChatId = useChatStore.use.selectedChatId();

  const { toast } = useToast();
  const posthog = usePostHog();

  const currentChat = getCurrentChat();
  const currentMessages = useMemo(
    () => currentChat?.messages || [],
    [currentChat],
  );

  useEffect(() => {
    const timer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }, 100);

    return () => clearTimeout(timer);
  }, [currentMessages]);

  const handleNegativeReaction = useCallback(
    (message: Message) => {
      posthog.capture("USER_REACTED_NEGATIVELY_TO_MESSAGE", {
        messageId: message.id,
        currentMessages,
      });
      setFeedbackMessage(message);
    },
    [posthog, currentMessages],
  );

  const handleFeedbackSubmit = useCallback(() => {
    posthog.capture("USER_SENT_FEEDBACK", {
      messageId: feedbackMessage?.id,
      currentMessages,
      reason: feedbackReason,
      details: feedbackDetails,
    });
    setFeedbackMessage(null);
    setFeedbackReason("");
    setFeedbackDetails("");
  }, [
    posthog,
    feedbackMessage,
    currentMessages,
    feedbackReason,
    feedbackDetails,
  ]);

  const handleCopyMessage = useCallback(
    (data: Data) => {
      const textToCopy = data.answer;
      navigator.clipboard.writeText(textToCopy).then(() => {
        toast({
          title: "Copied to clipboard",
          description: "The message has been copied to your clipboard.",
        });
      });
    },
    [toast],
  );

  const handleOnClickEditMessage = useCallback((message: Message) => {
    setEditMessageContent(message.data.answer);
    setIsEditable(message.id);
  }, []);

  const messageContent = useCallback((data: Data) => {
    console.log("data", data);
    if (data.url_supporting.length === 0) return data.answer;

    const formattedMessage = formatAnswerWithReferences(data);
    return formattedMessage.replace(/\n/g, "<br /s>");
  }, []);

  const handleOnEditMessage = useCallback(
    (messageId: string, newContent: string) => {
      if (!selectedChatId) {
        console.error("No current chat selected");
        return;
      }
      const messageToEdit = currentMessages.find(
        (message) => message.id === messageId,
      );
      if (messageToEdit) {
        const editedMessage: Message = {
          ...messageToEdit,
          data: { answer: newContent, url_supporting: [] },
        };
        sendMessage(editedMessage);
      }
    },
    [selectedChatId, sendMessage, currentMessages],
  );

  const handleOnSendEditMessage = useCallback(
    (dataId: string) => {
      if (!selectedChatId) {
        console.error("No current chat selected");
        return;
      }
      handleOnEditMessage(dataId, editMessageContent.trim());
      setEditMessageContent("");
      setIsEditable("");
    },
    [selectedChatId, editMessageContent, handleOnEditMessage],
  );
  return (
    <ScrollArea className="w-full overflow-y-auto overflow-x-hidden h-full flex flex-col absolute">
      {currentMessages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex flex-col gap-2 p-4",
            message.name === "Optimism GovGPT" ? "items-start" : "items-end",
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

            {message.name !== "Optimism GovGPT" &&
              isEditable !== message.id && (
                <Button
                  variant="ghost"
                  className="px-0"
                  size="sm"
                  onClick={() => handleOnClickEditMessage(message)}
                >
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
              )}

            <div
              className={cn(
                "p-3 rounded-md max-w-md overflow-hidden",
                "bg-accent",
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
                  {isEditable === message.id &&
                  message.name !== "Optimism GovGPT" ? (
                    <div key="input">
                      <Textarea
                        value={editMessageContent}
                        onChange={(e) => setEditMessageContent(e.target.value)}
                        className="min-w-96"
                      />
                      <div className="flex justify-end space-x-2 mt-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setIsEditable("")}
                        >
                          Cancel
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleOnSendEditMessage(message.id)}
                        >
                          Send
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <FormattedMessage content={messageContent(message.data)} />
                  )}
                  {!isStreaming && message.name === "Optimism GovGPT" && (
                    <div className="mt-2 flex gap-3 ">
                      <Button
                        variant="ghost"
                        className="px-0"
                        size="sm"
                        onClick={() => handleCopyMessage(message.data)}
                      >
                        <Clipboard className="h-3.5 w-3.5" />
                      </Button>
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
      <div ref={messagesEndRef} />
    </ScrollArea>
  );
});
