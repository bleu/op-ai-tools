"use client";

import React, { useEffect } from "react";
import { usePostHog } from "posthog-js/react";
import { TopicPageProps } from "@/app/forum/topic/[topicId]/page";

export function TopicTracker({
  topic,
  children,
}: TopicPageProps & { children: React.ReactNode }) {
  const posthog = usePostHog();

  useEffect(() => {
    posthog.capture("USER_ACCESSED_TOPIC", {
      categoryId: topic.category?.id,
      categoryExternalId: topic.category?.externalId,
      categoryName: topic.category?.name,
      topicId: topic.id,
      topicTitle: topic.title,
      topicUrl: topic.url,
    });
  }, []);

  return <>{children}</>;
}
