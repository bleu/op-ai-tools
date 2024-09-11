import { useCallback } from "react";
import { useToast } from "./use-toast";

interface UseCopyMessageResult {
  handleCopyMessage: (textToCopy: string) => Promise<void>;
}

export const useCopyMessage = (): UseCopyMessageResult => {
  const { toast } = useToast();

  const handleCopyMessage = useCallback(
    async (textToCopy: string): Promise<void> => {
      try {
        await navigator.clipboard.writeText(textToCopy);
        toast({
          title: "Copied to clipboard",
          description: "The message has been copied to your clipboard.",
        });
      } catch (error) {
        toast({
          title: "Copy failed",
          description: "Failed to copy the message to clipboard.",
          variant: "destructive",
        });
      }
    },
    [toast],
  );

  return { handleCopyMessage };
};
