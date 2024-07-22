import { InfiniteTable } from "../(components)/table";

export interface SearchParams {
  [key: string]: string | string[] | undefined;
}
export interface IndexPageProps {
  searchParams: SearchParams;
}

export default async function LatestPage({ searchParams }: IndexPageProps) {
  console.log({ searchParams });
  return <InfiniteTable title="Latest Topics" key="trending" />;
}
