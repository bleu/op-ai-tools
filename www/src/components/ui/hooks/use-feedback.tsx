import type React from "react";

import type { Message } from "@/app/data";
import { usePostHog } from "posthog-js/react";
import { useCallback, useState } from "react";
import { Button } from "../button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../dialog";
import { Label } from "../label";
import { RadioGroup, RadioGroupItem } from "../radio-group";
import { Textarea } from "../textarea";

export const useFeedback = (message: Message) => {
  const [feedbackReason, setFeedbackReason] = useState<string>("");
  const [feedbackDetails, setFeedbackDetails] = useState<string>("");
  const posthog = usePostHog();

  const handleNegativeReaction = useCallback(() => {
    posthog.capture("USER_REACTED_NEGATIVELY_TO_MESSAGE", {
      messageId: message.id,
    });
  }, [posthog, message.id]);

  const handleFeedbackSubmit = useCallback(() => {
    posthog.capture("USER_SENT_FEEDBACK", {
      messageId: message.id,
      reason: feedbackReason,
      details: feedbackDetails,
    });
    setFeedbackReason("");
    setFeedbackDetails("");
  }, [posthog, message.id, feedbackReason, feedbackDetails]);

  const FeedbackDialog: React.FC<{ trigger: React.ReactNode }> = ({
    trigger,
  }) => (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>What's wrong with this response?</DialogTitle>
        </DialogHeader>
        <RadioGroup onValueChange={setFeedbackReason} value={feedbackReason}>
          {["incomplete", "inaccurate", "unrelated", "outdated", "other"].map(
            (reason) => (
              <div key={reason} className="flex items-center space-x-2">
                <RadioGroupItem value={reason} id={reason} />
                <Label htmlFor={reason}>
                  {reason.charAt(0).toUpperCase() + reason.slice(1)}
                </Label>
              </div>
            ),
          )}
        </RadioGroup>
        <Textarea
          placeholder="Give us some more details..."
          value={feedbackDetails}
          onChange={(e) => setFeedbackDetails(e.target.value)}
        />
        <DialogClose asChild>
          <Button onClick={handleFeedbackSubmit}>Submit Feedback</Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  );

  return { handleNegativeReaction, FeedbackDialog };
};
