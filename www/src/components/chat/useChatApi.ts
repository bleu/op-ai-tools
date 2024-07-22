import { usePostHog } from "posthog-js/react";
import { useCallback } from "react";

export function useChatApi() {
  const posthog = usePostHog();

  const sendMessage = useCallback(
    async (message: string) => {
      if (!process.env.NEXT_PUBLIC_CHAT_STREAMING_API_URL) {
        throw new Error("Chat API URL is not defined");
      }

      const response = await fetch(
        process.env.NEXT_PUBLIC_CHAT_STREAMING_API_URL,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-user-id": posthog.get_distinct_id(),
          },
          body: JSON.stringify({ question: message }),
        }
      );

      if (!response.body) {
        throw new Error("No response body");
      }

      return response.body.getReader();
    },
    [posthog]
  );

  return { sendMessage };
}
