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
  about: string;
  status?: "Ongoing" | "Completed" | "Pending";
  category: string;
  author?: string;
  tldr: string;
  readTime?: string;
  created_at: string;
  lastActivity?: string;
};

export type ForumPostApiResponse = {
  data: ForumPost[];
  meta: {
    totalRowCount: number;
  };
};
