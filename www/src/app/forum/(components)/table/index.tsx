"use client";
import React from "react";

import {
  getCoreRowModel,
  getSortedRowModel,
  OnChangeFn,
  Row,
  ColumnFiltersState,
  useReactTable,
} from "@tanstack/react-table";
import {
  keepPreviousData,
  QueryClient,
  QueryClientProvider,
  useInfiniteQuery,
} from "@tanstack/react-query";
import { useVirtualizer } from "@tanstack/react-virtual";
import { SnapshotProposal } from "./table-row";
import { Separator } from "@/components/ui/separator";
import { FilterSelect } from "./filter-select";
import { FilterDates } from "./filter-dates";
import {
  FILTER_OPTIONS,
  ForumPost,
  ForumPostApiResponse,
} from "./post-options";

const FETCH_SIZE = 10;

async function getPosts({ pageParam }: { pageParam: number }) {
  const start = (pageParam as number) * FETCH_SIZE;

  const response = await fetch(
    "/api/forum-posts?start=" + start + "&size=" + FETCH_SIZE
  );
  const data = await response.json();
  return data;
}

function ForumInfiniteScrollTable({ title }: { title: string }) {
  const tableContainerRef = React.useRef<HTMLDivElement>(null);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  );

  const { data, fetchNextPage, isFetching, isLoading } =
    useInfiniteQuery<ForumPostApiResponse>({
      queryKey: ["forumPosts"],
      queryFn: getPosts as any,
      initialPageParam: 0,
      getNextPageParam: (_lastGroup, groups) => groups.length,
      refetchOnWindowFocus: false,
      placeholderData: keepPreviousData,
    });

  // flatten the array of arrays from the useInfiniteQuery hook
  const flatData = React.useMemo(
    () => data?.pages?.flatMap((page) => page.data) ?? [],
    [data]
  );

  const totalDBRowCount = data?.pages?.[0]?.meta?.totalRowCount ?? 0;
  const totalFetched = flatData.length;

  // called on scroll and possibly on mount to fetch more data as the user scrolls and reaches bottom of table
  const fetchMoreOnBottomReached = React.useCallback(
    (containerRefElement?: HTMLDivElement | null) => {
      if (containerRefElement) {
        const { scrollHeight, scrollTop, clientHeight } = containerRefElement;
        // once the user has scrolled within 500px of the bottom of the table, fetch more data if we can
        if (
          scrollHeight - scrollTop - clientHeight < 500 &&
          !isFetching &&
          totalFetched < totalDBRowCount
        ) {
          fetchNextPage();
        }
      }
    },
    [fetchNextPage, isFetching, totalFetched, totalDBRowCount]
  );

  // a check on mount and after a fetch to see if the table is already scrolled to the bottom and immediately needs to fetch more data
  React.useEffect(() => {
    fetchMoreOnBottomReached(tableContainerRef.current);
  }, [fetchMoreOnBottomReached]);

  const table = useReactTable({
    data: flatData,
    columns: [
      {
        accessorKey: "category",
      },
    ],
    state: {
      columnFilters,
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    manualSorting: true,
    debugTable: true,
  });

  // scroll to top of table when sorting changes
  const handleColumnFilterChange: OnChangeFn<ColumnFiltersState> = (
    updater
  ) => {
    setColumnFilters(updater);
    if (!!table.getRowModel().rows.length) {
      rowVirtualizer.scrollToIndex?.(0);
    }
  };

  // since this table option is derived from table row model state, we're using the table.setOptions utility
  table.setOptions((prev) => ({
    ...prev,
    onColumnFiltersChange: handleColumnFilterChange,
  }));

  const { rows } = table.getRowModel();

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    estimateSize: () => 150, //estimate row height for accurate scrollbar dragging
    getScrollElement: () => tableContainerRef.current,
    // measure dynamic row height, except in firefox because it measures table border height incorrectly
    measureElement:
      typeof window !== "undefined" &&
      navigator.userAgent.indexOf("Firefox") === -1
        ? (element) => element?.getBoundingClientRect().height
        : undefined,
    overscan: 5,
  });

  if (isLoading) {
    return <>Loading...</>;
  }

  return (
    <div
      className="overflow-auto relative max-h-screen"
      onScroll={(e) => fetchMoreOnBottomReached(e.target as HTMLDivElement)}
      ref={tableContainerRef}
    >
      <div className="mx-4">
        <h1 className="text-2xl font-bold mb-6">{title}</h1>
        <div className="w-full flex gap-2 items-center pr-4 flex-col md:flex-row">
          <FilterSelect data={FILTER_OPTIONS} />
          <FilterDates />
        </div>
      </div>
      {/* Even though we're still using sematic table tags, we must use CSS grid and flexbox for dynamic row heights */}
      <table className="grid pt-2">
        <tbody
          className="grid relative"
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const row = rows[virtualRow.index] as Row<ForumPost>;
            return (
              <tr
                data-index={virtualRow.index} // needed for dynamic row height measurement
                ref={(node) => rowVirtualizer.measureElement(node)} //mmeasure dynamic row height
                key={row.id}
                style={{
                  transform: `translateY(${virtualRow.start}px)`, //this should always be a `style` as it changes on scroll
                }}
                className="flex absolute w-full"
              >
                <td className="flex w-full justify-center">
                  <div className="w-full">
                    <SnapshotProposal
                      id={row.original.id}
                      about={row.original.about}
                      status={row.original.status}
                      category={row.original.category}
                      author={row.original.author}
                      tldr={row.original.tldr}
                      readTime={row.original.readTime}
                      created_at={row.original.created_at}
                      lastActivity={row.original.lastActivity}
                    />
                    <Separator orientation="horizontal" className="max-w-6xl" />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
        {isFetching && (
          <div className="flex justify-center animate-pulse mt-1">
            Loading...
          </div>
        )}
      </table>
    </div>
  );
}

const queryClient = new QueryClient();

export function InfiniteTable({ title }: { title: string }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ForumInfiniteScrollTable title={title} />
    </QueryClientProvider>
  );
}
