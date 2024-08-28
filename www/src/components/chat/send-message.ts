import posthog from "posthog-js";

export async function sendMessage(
  message: string,
  memory: { name: string; message: string }[] = [],
) {
  if (!process.env.NEXT_PUBLIC_CHAT_API_URL) {
    throw new Error("Chat API URL is not defined");
  }

  const response = await fetch(process.env.NEXT_PUBLIC_CHAT_API_URL, {
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
}
