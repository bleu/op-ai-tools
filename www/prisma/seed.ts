import { PrismaClient } from "@prisma/client";
import fs from "fs";
import path from "path";

const prisma = new PrismaClient();

async function main() {
  const filePath = path.resolve(
    __dirname,
    "../../../op-ai-tools/data/summaries/all_thread_summaries.txt"
  );

  const data = fs.readFileSync(filePath, "utf-8");

  // Split the data into individual forum posts
  const posts = data
    .split(
      "--------------------------------------------------------------------------------"
    )
    .map((post) => post.trim())
    .filter((post) => post);

  for (const post of posts) {
    const urlMatch = post.match(/URL:\s*(.*)/);
    const categoryMatch = post.match(/<classification>(.*)<\/classification>/);
    const aboutMatch = post.match(/<about>\s*([\s\S]*?)<\/about>/);
    const firstPostMatch = post.match(
      /<first_post>\s*([\s\S]*?)<\/first_post>/
    );
    const reactionMatch = post.match(/<reaction>\s*([\s\S]*?)<\/reaction>/);
    const overviewMatch = post.match(/<overview>\s*([\s\S]*?)<\/overview>/);
    const tldrMatch = post.match(/<tldr>\s*([\s\S]*?)<\/tldr>/);

    await prisma.forumPost.create({
      data: {
        url: urlMatch ? urlMatch[1].trim() : "",
        category: categoryMatch ? categoryMatch[1].trim() : "",
        about: aboutMatch ? aboutMatch[1].trim() : "",
        firstPost: firstPostMatch ? firstPostMatch[1].trim() : "",
        reaction: reactionMatch ? reactionMatch[1].trim() : "",
        overview: overviewMatch ? overviewMatch[1].trim() : "",
        tldr: tldrMatch ? tldrMatch[1].trim() : "",
      },
    });
  }

  console.log("Seeding completed!");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
