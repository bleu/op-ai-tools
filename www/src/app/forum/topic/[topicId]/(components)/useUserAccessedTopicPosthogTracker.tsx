"use client";

import React, { useEffect } from "react";
import { usePostHog } from "posthog-js/react";
import { TopicPageProps } from "@/app/forum/topic/[topicId]/page";

export function useUserAccessedTopicPosthogTracker(
  topic?: TopicPageProps["topic"]
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
  }, [topic]);

  return null;
}
