import { PrismaClient } from "@prisma/client";
import fs from "fs";
import path from "path";
import readline from "readline";

const prisma = new PrismaClient();

interface ForumThread {
  generator: string;
  version: string;
  extractor: string;
  download_time: string;
  type: string;
  item: {
    path: string[];
    url: string;
    origin: string;
    data: {
      id: number;
      name?: string;
      username?: string;
      display_username?: string;
      title: string;
      fancy_title: string;
      slug: string;
      posts_count: number;
      reply_count: number;
      highest_post_number: number;
      image_url: string | null;
      created_at: string;
      last_posted_at: string;
      bumped: boolean;
      bumped_at: string;
      archetype: string;
      unseen: boolean;
      pinned: boolean;
      unpinned: string | null;
      excerpt: string;
      visible: boolean;
      closed: boolean;
      archived: boolean;
      bookmarked: string | null;
      liked: string | null;
      tags: string[];
      tags_descriptions: Record<string, string>;
      views: number;
      like_count: number;
      has_summary: boolean;
      last_poster_username: string;
      category_id: number;
      pinned_globally: boolean;
      featured_link: string | null;
      has_accepted_answer: boolean;
      can_vote: boolean;
      posters: Array<{
        extras: string | null;
        description: string;
        user_id: number;
        primary_group_id: number | null;
        flair_group_id: number | null;
      }>;
    };
    title: string;
  };
}

const findByUrl = (
  url: string,
  data: ForumThread[],
  posttype: string = "thread"
): ForumThread => {
  // @ts-ignore
  return data.find((obj) => obj.type === posttype && obj.item.url === url);
};

const findAuthorByUrl = (url: string, data: ForumThread[]) => {
  const obj = findByUrl(url + "/1", data, "post");

  if (obj) {
    return {
      username: obj.item.data.username,
      display_username: obj.item.data.display_username,
    };
  }

  return {};
};

async function getOutObject() {
  // create a readline interface for reading the file line by line
  const outFilePath = path.resolve(
    __dirname,
    "../../../op-ai-tools/data/002-governance-forum-202406014/dataset/_out.jsonl"
  );
  const outFileStream = fs.createReadStream(outFilePath);

  const outRl = readline.createInterface({
    input: outFileStream,
    crlfDelay: Infinity,
  });

  // object to store out.jsonl data
  const outObject = [];

  for await (const line of outRl) {
    if (line.trim()) {
      try {
        const obj = JSON.parse(line);
        outObject.push(obj);
      } catch (error) {
        console.error(`Error parsing line: ${line}`);
        console.error(error);
      }
    }
  }

  return outObject;
}

function getCategories() {
  const categoriesFilePath = path.resolve(
    __dirname,
    "../../../op-ai-tools/data/discourse/categories.json"
  );

  var data = JSON.parse(fs.readFileSync(categoriesFilePath, "utf8"));
  return data.category_list.categories;
}

function getCategoryNameById(obj: any, category_id: Number) {
  // Find the category with the given ID
  // @ts-ignore
  const category = obj.find((category) => category.id === category_id);

  if (category) {
    return category.name;
  } else {
    return "Category not found for ID: " + category_id;
  }
}

async function main() {
  const outObject = await getOutObject();
  const categories = getCategories();

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
    // const categoryMatch = post.match(/<classification>(.*)<\/classification>/);
    const aboutMatch = post.match(/<about>\s*([\s\S]*?)<\/about>/);
    const firstPostMatch = post.match(
      /<first_post>\s*([\s\S]*?)<\/first_post>/
    );
    const reactionMatch = post.match(/<reaction>\s*([\s\S]*?)<\/reaction>/);
    const overviewMatch = post.match(/<overview>\s*([\s\S]*?)<\/overview>/);
    const tldrMatch = post.match(/<tldr>\s*([\s\S]*?)<\/tldr>/);

    const url = urlMatch ? urlMatch[1].trim() : "";

    const threadPost = findByUrl(url, outObject);
    const author = findAuthorByUrl(url, outObject);
    const categoryLabel = getCategoryNameById(
      categories,
      threadPost.item.data.category_id
    );

    const forumPostData = {
      title: threadPost.item.title,
      url: threadPost.item.url,
      lastPostedAt: threadPost.item.data.last_posted_at,
      createdAt: threadPost.item.data.created_at,
      externalId: threadPost.item.data.id,
      category: categoryLabel,
      summary: aboutMatch ? aboutMatch[1].trim() : "",
      firstPost: firstPostMatch ? firstPostMatch[1].trim() : "",
      reaction: reactionMatch ? reactionMatch[1].trim() : "",
      overview: overviewMatch ? overviewMatch[1].trim() : "",
      tldr: tldrMatch ? tldrMatch[1].trim() : "",
      username: author.username,
      displayUsername: author.display_username,
    };

    console.log(forumPostData);

    // await prisma.forumPost.create({
    //   data: forumPostData
    // });
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
