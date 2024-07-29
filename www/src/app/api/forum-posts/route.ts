import prisma from "@/lib/prisma";
import { type NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  // @ts-ignore
  const params = req.nextUrl.searchParams;

  const start = params.get("start");
  const pageSize = params.get("size");
  const category = params.get("category");
  const startDate = params.get("startDate");
  const endDate = params.get("endDate");

  // // Build the query conditions
  // const conditions: any = {};

  // if (category) {
  //   conditions.category = category;
  // }

  // if (startDate && endDate) {
  //   conditions.createdAt = {
  //     gte: new Date(startDate),
  //     lte: new Date(endDate),
  //   };
  // } else if (startDate) {
  //   conditions.createdAt = {
  //     gte: new Date(startDate),
  //   };
  // } else if (endDate) {
  //   conditions.createdAt = {
  //     lte: new Date(endDate),
  //   };
  // }

  const forumPosts = await prisma.forumPost.findMany({
    skip: start ? Number(start) : 0,
    take: pageSize ? Number(pageSize) : 10,
    // where: conditions,
    //   orderBy: {
    //     createdAt: 'desc', // Order by created date
    //   },
    // include: {
    //   category: {
    //     select: {
    //       name: true
    //     }
    //   }
    // }
  });

  const categories = await prisma.forumPostCategory.findMany();

  const data = forumPosts.map((post) => ({
    ...post,
    category:
      categories.find((category) => category.id == post.category)?.name || null,
  }));

  const totalRowCount = await prisma.forumPost.count({
    // where: conditions,
  });

  return NextResponse.json({
    data,
    meta: {
      totalRowCount,
    },
  });
}
