import prisma from "@/lib/prisma";
import { type NextRequest, NextResponse } from "next/server";

const parseCategory = (
  categoryExternalId: string,
  filterableCategories: number[],
) => {
  if (categoryExternalId === "all") {
    return undefined;
  }

  if (categoryExternalId === "others") {
    return {
      id: {
        notIn: filterableCategories,
      },
    };
  }

  return {
    externalId: categoryExternalId,
  };
};

export async function GET(req: NextRequest) {
  const params = req.nextUrl.searchParams;

  const start = params.get("start");
  const pageSize = params.get("size");
  const category = params.get("category");
  const startDate = params.get("startDate");
  const endDate = params.get("endDate");

  // Build the query conditions
  const conditions: any = {};

  const filterableCategories = await prisma.forumPostCategory
    .findMany({
      where: {
        filterable: true,
      },
      select: {
        id: true,
      },
    })
    .then((categories) => categories.map((category) => category.id));

  if (category) {
    const parsedCategory = parseCategory(category, filterableCategories);
    if (parsedCategory) {
      conditions.category = {
        ...parsedCategory,
      };
    }
  }

  // if (startDate || endDate) {
  //   conditions.createdAt = {};
  //   if (startDate) {
  //     conditions.createdAt.gte = new Date(startDate);
  //   }
  //   if (endDate) {
  //     conditions.createdAt.lte = new Date(endDate);
  //   }
  // }

  const data = await prisma.forumPost.findMany({
    skip: start ? Number(start) : 0,
    take: pageSize ? Number(pageSize) : 10,
    include: {
      category: {
        select: {
          id: true,
          name: true,
          externalId: true,
        },
      },
    },
    where: conditions,
    orderBy: {
      lastActivity: "desc",
    },
  });

  const totalRowCount = await prisma.forumPost.count({
    where: conditions,
  });

  return NextResponse.json({
    data,
    meta: {
      totalRowCount,
    },
  });
}
