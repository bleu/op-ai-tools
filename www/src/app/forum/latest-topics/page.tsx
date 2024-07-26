import { InfiniteTable } from "@/components/forum/table";
import prisma from "@/lib/prisma";

export interface SearchParams {
  [key: string]: string | string[] | undefined;
}
export interface IndexPageProps {
  searchParams: SearchParams;
}

export default async function LatestPage({ searchParams }: IndexPageProps) {
  const categories = await prisma.forumPostCategory.findMany({
    select: {
      id: true,
      name: true,
      color: true,
    },
  });

  const renamedCategories = categories.map((category) => ({
    value: category.id,
    label: category.name,
    color: category.color,
  }));

  return (
    <InfiniteTable
      title="Latest Topics"
      key="trending"
      categories={renamedCategories}
    />
  );
}
