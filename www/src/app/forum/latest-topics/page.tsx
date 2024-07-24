import { InfiniteTable } from "@/components/forum/table";

export interface SearchParams {
  [key: string]: string | string[] | undefined;
}
export interface IndexPageProps {
  searchParams: SearchParams;
}

export default async function LatestPage({ searchParams }: IndexPageProps) {
  return <InfiniteTable title="Latest Topics" key="trending" />;
}
