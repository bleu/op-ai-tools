import { InfiniteTable } from "../(components)/table";

export default function TrendingPage() {
  return (
    <InfiniteTable title="Trending Topics" fetchPath="TODO" key="latest" />
  );
}
