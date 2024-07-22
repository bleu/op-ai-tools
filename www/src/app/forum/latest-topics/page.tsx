import { InfiniteTable } from "../(components)/table";

export default function LatestPage() {
  return (
    <InfiniteTable title="Latest Topics" fetchPath="TODO" key="trending" />
  );
}
