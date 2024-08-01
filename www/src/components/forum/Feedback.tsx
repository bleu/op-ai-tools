import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/hooks/use-toast";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { ThumbsDownIcon, ThumbsUpIcon } from "lucide-react";
import { usePostHog } from "posthog-js/react";
import { useState } from "react";
import { useForm } from "react-hook-form";

type FeedbackReason = "incomplete" | "unrelated" | "outdated" | "incorrect";

type FeedbackFormData = {
  details: string;
  username?: string;
};

export function Feedback({
  id,
  title,
  url,
  categoryId,
}: {
  id: number;
  url: string;
  title: string;
  categoryId?: number;
}) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedReasons, setSelectedReasons] = useState<FeedbackReason[]>([]);
  const [validationError, setValidationError] = useState<string | null>(null);
  const { register, handleSubmit, reset } = useForm<FeedbackFormData>();
  const posthog = usePostHog();
  const { toast } = useToast();

  const handlePositiveFeedback = () => {
    posthog.capture("USER_REACTED_POSITIVELY_TO_SUMMARY", {
      topicId: id,
      topicTitle: title,
      topicUrl: url,
      categoryId,
    });

    toast({
      title: "Thank you for your feedback!",
      description: "We're glad you found this helpful.",
    });
  };

  const toggleReason = (reason: FeedbackReason) => {
    setSelectedReasons((prev) =>
      prev.includes(reason)
        ? prev.filter((r) => r !== reason)
        : [...prev, reason],
    );
    setValidationError(null);
  };

  const onSubmit = (data: FeedbackFormData) => {
    if (selectedReasons.length === 0 && !data.details.trim()) {
      setValidationError(
        "Please select at least one reason or provide details.",
      );
      return;
    }

    posthog.capture("USER_REACTED_NEGATIVELY_TO_SUMMARY", {
      reasons: selectedReasons,
      feedbackDetails: data.details,
      username: data.username,
      topicId: id,
      topicUrl: url,
      topicTitle: title,
      categoryId,
    });

    toast({
      title: "Thank you for your feedback!",
      description:
        "We appreciate your input and will carefully look into this.",
    });

    setIsDialogOpen(false);
    setSelectedReasons([]);
    setValidationError(null);
    reset();
  };

  return (
    <>
      <span className="text-sm">Was this helpful?</span>
      <Button
        variant="ghost"
        size="icon"
        className="w-fit"
        onClick={handlePositiveFeedback}
      >
        <ThumbsUpIcon className="h-4 w-4" />
      </Button>
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Button variant="ghost" size="icon" className="w-fit">
            <ThumbsDownIcon className="h-4 w-4" />
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>What's wrong?</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="grid md:grid-cols-2 gap-4 py-4">
              {[
                { value: "incomplete", label: "Incomplete" },
                { value: "unrelated", label: "Not related to category/topic" },
                { value: "outdated", label: "Outdated" },
                { value: "incorrect", label: "Incorrect information" },
              ].map((reason) => (
                <Button
                  key={reason.value}
                  type="button"
                  variant={
                    selectedReasons.includes(reason.value as FeedbackReason)
                      ? "default"
                      : "outline"
                  }
                  onClick={() => toggleReason(reason.value as FeedbackReason)}
                  className={cn(
                    "justify-start hover:bg-[#FFDBDF]",
                    selectedReasons.includes(reason.value as FeedbackReason) &&
                      "bg-optimism hover:text-optimism",
                  )}
                >
                  {reason.label}
                </Button>
              ))}
            </div>
            <Input
              {...register("username")}
              placeholder="Your username (optional)"
              className="mt-4"
              onChange={() => setValidationError(null)}
            />
            <Textarea
              {...register("details")}
              placeholder="Give us some more details"
              className="mt-4"
              onChange={() => setValidationError(null)}
            />
            {validationError && (
              <p className="text-red-500 text-sm mt-2">{validationError}</p>
            )}
            <Button
              type="submit"
              className="mt-4 w-full bg-optimism text-white hover:bg-optimism/80"
            >
              Send feedback
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
