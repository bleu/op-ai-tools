import { useCallback } from "react";

import { useToast } from "./use-toast";

export const useCopyMessage = () => {
  const { toast } = useToast();

  const handleCopyMessage = useCallback(
    (textToCopy: string) => {
      navigator.clipboard.writeText(textToCopy).then(() => {
        toast({
          title: "Copied to clipboard",
          description: "The message has been copied to your clipboard.",
        });
      });
    },
    [toast],
  );

  return { handleCopyMessage };
};
