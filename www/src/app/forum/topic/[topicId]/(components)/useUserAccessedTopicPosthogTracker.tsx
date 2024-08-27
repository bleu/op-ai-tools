"use client";

import type { TopicPageProps } from "@/app/forum/topic/[topicId]/page";
import { usePostHog } from "posthog-js/react";
import React, { useEffect } from "react";

export function useUserAccessedTopicPosthogTracker(
  topic?: TopicPageProps["topic"],
) {
  const posthog = usePostHog();

  useEffect(() => {
    if (!topic) return;

    posthog.capture("USER_ACCESSED_TOPIC", {
      categoryId: topic.category?.id,
      categoryExternalId: topic.category?.externalId,
      categoryName: topic.category?.name,
      topicId: topic.id,
      topicTitle: topic.title,
      topicUrl: topic.url,
    });
  }, [topic, posthog.capture]);

  return null;
}
