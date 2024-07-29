export const FILTER_OPTIONS = {
  label: "Filter by category",
  options: [
    { label: "All", value: "all" },
    { label: "Delegates", value: 41 },
    { label: "General Discussions", value: 1 },
    { label: "Mission Grants", value: 69 },
    { label: "Updates and Announcements", value: 48 },
    { label: "Retro Funding", value: 46 },
    { label: "Others", value: "others" },
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
