import Link from "next/link";
import React from "react";
import { usePostHog } from "posthog-js/react";

export function TopicLink({
  id,
  title,
  category,
  children,
}: {
  id: number;
  title: string;
  category: {
    id: number;
    externalId: string;
    name: string;
  };
  children: React.ReactNode;
}) {
  const posthog = usePostHog();

  function handleLinkClick() {
    posthog.capture("USER_ACCESSED_SUMMARY", {
      categoryId: category.id,
      categoryExternalId: category.externalId,
      categoryName: category.name,
      topicId: id,
      topicTitle: title,
    });
  }

  return (
    <Link href={`/forum/topic/${id}`} onClick={handleLinkClick}>
      {children}
    </Link>
  );
}
