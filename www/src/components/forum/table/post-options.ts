export const FILTER_OPTIONS = {
  label: "Filter by category",
  options: [
    { label: "All", value: "all" },
    { label: "General Discussions", value: "discussion" },
    { label: "Informative", value: "informative" },
    { label: "Feedback", value: "feedback" },
    { label: "Updates and Announcements", value: "announcement" },
    { label: "Unimportant", value: "unimportant" },
    { label: "Guide", value: "guide" },
  ],
};

export type ForumPost = {
  id?: number;
  external_id?: string;
  url?: string;
  title?: string;
  username?: string;
  displayUsername?: string;
  category?: string;
  about?: string;
  firstPost?: string;
  reaction?: string;
  overview?: string;
  tldr?: string;
  createdAt?: string;
  updatedAt?: string;
  status?: string;
};

export type ForumPostApiResponse = {
  data: ForumPost[];
  meta: {
    totalRowCount: number;
  };
};
