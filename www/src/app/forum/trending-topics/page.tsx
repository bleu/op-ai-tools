import { InfiniteTable } from "@/components/forum/table";

export interface SearchParams {
  [key: string]: string | string[] | undefined;
}
export interface IndexPageProps {
  searchParams: SearchParams;
}

export default async function TrendingPage({ searchParams }: IndexPageProps) {
  const { category, startDate, endDate } = searchParams;

  return (
    <InfiniteTable
      title="Trending Topics"
      key="trending"
      category={category as string}
      startDate={startDate as string}
      endDate={endDate as string}
    />
  );
}
