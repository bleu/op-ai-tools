import { useState } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { ThumbsDownIcon, ThumbsUpIcon } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type FeedbackReason = "incomplete" | "unrelated" | "outdated" | "incorrect";

type FeedbackFormData = {
  details: string;
};

export function Feedback() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedReasons, setSelectedReasons] = useState<FeedbackReason[]>([]);
  const [validationError, setValidationError] = useState<string | null>(null);
  const { register, handleSubmit, reset } = useForm<FeedbackFormData>();

  const handlePositiveFeedback = () => {
    console.log("Positive feedback received");
  };

  const toggleReason = (reason: FeedbackReason) => {
    setSelectedReasons((prev) =>
      prev.includes(reason)
        ? prev.filter((r) => r !== reason)
        : [...prev, reason]
    );
    setValidationError(null);
  };

  const onSubmit = (data: FeedbackFormData) => {
    if (selectedReasons.length === 0 && !data.details.trim()) {
      setValidationError(
        "Please select at least one reason or provide details."
      );
      return;
    }

    const feedbackData = {
      ...data,
      reasons: selectedReasons,
    };
    console.log("Feedback submitted:", feedbackData);
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
            <div className="grid grid-cols-2 gap-4 py-4">
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
                      "bg-optimism hover:text-optimism"
                  )}
                >
                  {reason.label}
                </Button>
              ))}
            </div>
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
