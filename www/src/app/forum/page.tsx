import { redirect } from "next/navigation";

export interface SearchParams {
  [key: string]: string | string[] | undefined;
}
export interface IndexPageProps {
  searchParams: SearchParams;
}

export default function ForumPage({ searchParams }: IndexPageProps) {
  const { category } = searchParams;

  return redirect(
    `/forum/latest-topics?${category ? `category=${category}` : ""}`
  );
}
