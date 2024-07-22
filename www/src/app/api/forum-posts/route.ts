import type { NextApiRequest } from "next";
import prisma from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET(req: NextApiRequest) {
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

  const data = await prisma.forumPost.findMany({
    skip: start ? Number(start) : 0,
    take: pageSize ? Number(pageSize) : 10,
    // where: conditions,
    //   orderBy: {
    //     createdAt: 'desc', // Order by created date
    //   },
  });

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
