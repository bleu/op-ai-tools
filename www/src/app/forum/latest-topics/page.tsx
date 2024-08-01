import { InfiniteTable } from "@/components/forum/table";

export interface SearchParams {
  [key: string]: string | string[] | undefined;
}
export interface IndexPageProps {
  searchParams: SearchParams;
}

export default async function LatestPage({ searchParams }: IndexPageProps) {
  const { category, startDate, endDate } = searchParams;

  return (
    <InfiniteTable
      title="Latest Topics"
      key="latest"
      category={category as string}
      startDate={startDate as string}
      endDate={endDate as string}
    />
  );
}
