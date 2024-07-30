export const FILTER_OPTIONS = {
  label: "Filter by category",
  options: [
    { label: "All", value: "all", slug: "all" },
    { label: "Delegates", value: "41", slug: "delegates" },
    { label: "General Discussions", value: "1", slug: "general" },
    { label: "Mission Grants", value: "69", slug: "grants" },
    { label: "Updates and Announcements", value: "48", slug: "updates" },
    { label: "Retro Funding", value: "46", slug: "retro-funding" },
    { label: "Others", value: "others", slug: "others" },
  ],
};

export const CATEGORY_BY_SLUG: { [key: string]: string } = FILTER_OPTIONS.options.reduce(
  (acc, option) => ({
    ...acc,
    [option.slug]: option.value,
  }),
  {}
);

export const categoryBySlug = (slug: string): string => CATEGORY_BY_SLUG[slug] || "";

export type ForumPost = {
  id?: number;
  externalId?: string;
  url?: string;
  title?: string;
  username?: string;
  displayUsername?: string;
  categoryId?: number;
  rawForumPostId?: number;
  about?: string;
  reaction?: string;
  overview?: string;
  tldr?: string;
  createdAt?: string;
  updatedAt?: string;
  category?: {
    id: number;
    name: string;
    externalId: string;
  };
  status?: string;
  readTime?: string;
  lastActivity?: string;
};

export type ForumPostApiResponse = {
  data: ForumPost[];
  meta: {
    totalRowCount: number;
  };
};
