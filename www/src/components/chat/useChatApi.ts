import { usePostHog } from "posthog-js/react";
import { useCallback } from "react";

export function useChatApi() {
  const posthog = usePostHog();

  const sendMessage = useCallback(
    async (
      message: string,
      memory: { name: string; message: string }[] = [],
    ) => {
      if (!process.env.NEXT_PUBLIC_CHAT_API_URL) {
        throw new Error("Chat API URL is not defined");
      }

      const response = await fetch("http://localhost:9090/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-user-id": posthog.get_distinct_id(),
        },
        body: JSON.stringify({ question: message, memory }),
      });

      if (!response.body) {
        throw new Error("No response body");
      }

      return await response.json();
    },
    [posthog],
  );

  return { sendMessage };
}
