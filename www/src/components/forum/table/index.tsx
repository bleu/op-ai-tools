"use client";
import React, { useCallback, useEffect } from "react";

import { Separator } from "@/components/ui/separator";
import {
  QueryClient,
  QueryClientProvider,
  keepPreviousData,
  useInfiniteQuery,
} from "@tanstack/react-query";
import {
  type ColumnFiltersState,
  type OnChangeFn,
  type Row,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { FilterSelect } from "./filter-select";
import {
  FILTER_OPTIONS,
  type Topic,
  type TopicApiResponse,
} from "./post-options";
import { SnapshotProposal } from "./table-row";

import { DateRangePicker } from "@/components/ui/date-range-picker";
import type { DateRange } from "react-day-picker";

const FETCH_SIZE = 10;

function toLocaleDateString(date: Date | undefined) {
  if (!date) {
    return undefined;
  }

  return date.toLocaleDateString("en-US");
}

async function getPosts({
  pageParam,
}: {
  pageParam: {
    page: number;
    category: string;
    startDate: string;
    endDate: string;
  };
}) {
  const { page, category, startDate, endDate } = pageParam;
  const start = page * FETCH_SIZE;

  const params = new URLSearchParams({
    start: start.toString(),
    size: FETCH_SIZE.toString(),
    category,
    ...(startDate && { startDate }),
    ...(endDate && { endDate }),
  });

  const response = await fetch(`/api/forum-posts?${params.toString()}`);
  const data = await response.json();
  return data;
}

function ForumInfiniteScrollTable({
  title,
  category,
  startDate,
  endDate,
}: {
  title: string;
  category?: string;
  startDate?: Date;
  endDate?: Date;
}) {
  const tableContainerRef = React.useRef<HTMLDivElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const [dates, setDates] = React.useState<DateRange | undefined>({
    from: startDate || undefined,
    to: endDate || undefined,
  });

  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([
    {
      id: "category",
      value: category || "all",
    },
  ]);

  const { data, fetchNextPage, isFetching, isLoading } =
    useInfiniteQuery<TopicApiResponse>({
      queryKey: ["topics", columnFilters, dates], // refetch when filters changes
      queryFn: getPosts as any,
      initialPageParam: {
        page: 0,
        category: columnFilters.find((f) => f.id === "category")?.value,
        startDate: toLocaleDateString(dates?.from),
        endDate: toLocaleDateString(dates?.to),
      },
      getNextPageParam: (_lastGroup, groups) => {
        return {
          page: groups.length,
          category: columnFilters.find((f) => f.id === "category")?.value,
          startDate: toLocaleDateString(dates?.from),
          endDate: toLocaleDateString(dates?.to),
        };
      },
      refetchOnWindowFocus: false,
      placeholderData: keepPreviousData,
    });

  // flatten the array of arrays from the useInfiniteQuery hook
  const flatData = React.useMemo(
    () => data?.pages?.flatMap((page) => page.data) ?? [],
    [data],
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
    [fetchNextPage, isFetching, totalFetched, totalDBRowCount],
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
    updater,
  ) => {
    setColumnFilters(updater);
    if (table.getRowModel().rows.length) {
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

  // https://nextjs.org/docs/app/api-reference/functions/use-search-params#updating-searchparams
  const createQueryString = useCallback(
    (paramsObject: { [s: string]: unknown } | ArrayLike<unknown>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(paramsObject).forEach(([name, value]) => {
        if (value) {
          params.set(name, String(value));
        } else {
          params.delete(name);
        }
      });

      return params.toString();
    },
    [searchParams],
  );

  const onCategoryFilterChange = (value: string, setParams = true) => {
    if (setParams) {
      const query = {
        category: value,
        startDate: toLocaleDateString(dates?.from),
        endDate: toLocaleDateString(dates?.to),
      };
      router.push(`${pathname}?${createQueryString(query)}`);
    }
    setColumnFilters([
      {
        id: "category",
        value,
      },
    ]);
  };

  useEffect(() => {
    if (category) {
      onCategoryFilterChange(category, false);
    }

    const query = {
      category: category,
      startDate: toLocaleDateString(dates?.from),
      endDate: toLocaleDateString(dates?.to),
    };

    router.push(`${pathname}?${createQueryString(query)}`);
  }, [category, dates]);

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
        <div className="w-full flex gap-2 items-center flex-col md:flex-row">
          <FilterSelect
            data={FILTER_OPTIONS}
            value={
              columnFilters.find((f) => f.id === "category")?.value as string
            }
            onChange={onCategoryFilterChange}
          />
          <DateRangePicker
            className="bg-muted"
            dateRange={dates}
            setDateRange={setDates}
          />
        </div>
      </div>
      {/* Even though we're still using sematic table tags, we must use CSS grid and flexbox for dynamic row heights */}
      <table className="grid pt-2">
        <tbody
          className="grid relative mx-4"
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const row = rows[virtualRow.index] as Row<Topic>;
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
                      url={row.original.url}
                      title={row.original.title}
                      username={row.original.username}
                      displayUsername={row.original.displayUsername}
                      readTime={row.original.readTime}
                      lastActivity={row.original.lastActivity}
                      category={row.original.category}
                      about={row.original.about}
                      createdAt={row.original.createdAt}
                      updatedAt={row.original.updatedAt}
                      status={row.original.status}
                    />
                    <Separator
                      orientation="horizontal"
                      className="max-w-7xl mt-1"
                    />
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

export function InfiniteTable({
  title,
  category,
  startDate,
  endDate,
}: {
  title: string;
  category?: string;
  startDate?: string;
  endDate?: string;
}) {
  const from = startDate ? new Date(startDate) : undefined;
  const to = endDate ? new Date(endDate) : undefined;

  return (
    <QueryClientProvider client={queryClient}>
      <ForumInfiniteScrollTable
        title={title}
        category={category}
        startDate={from}
        endDate={to}
      />
    </QueryClientProvider>
  );
}
