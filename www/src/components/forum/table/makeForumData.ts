import { faker } from "@faker-js/faker";

const categories = [
  "Delegates",
  "General Discussions",
  "Mission Grants",
  "Updates and Announcements",
  "Retro Funding",
  "Others",
];
export type ForumPost = {
  id: number;
  title: string;
  status: "Ongoing" | "Completed" | "Pending";
  category: string;
  author: string;
  summary: string;
  readTime: string;
  date: Date;
  lastActivity: string;
  proposal: string;  
  userOpinions: string[]; 
  originalContent: {
    url: string;
    text: string;
  }[]; 
};

export type ForumPostApiResponse = {
  data: ForumPost[];
  meta: {
    totalRowCount: number;
  };
};

const range = (len: number) => {
  const arr: number[] = [];
  for (let i = 0; i < len; i++) {
    arr.push(i);
  }
  return arr;
};

const newForumPost = (index: number): ForumPost => {
  return {
    id: index + 1,
    title: faker.lorem.sentence(3),
    status: faker.helpers.shuffle<ForumPost["status"]>([
      "Ongoing",
      "Completed",
      "Pending",
    ])[0]!,
    category: faker.helpers.shuffle(categories)[0]!,
    author: faker.person.fullName(),
    summary: faker.lorem.paragraph(),
    readTime: `${faker.number.int({ min: 1, max: 15 })} min read`,
    date: faker.date.anytime(),
    lastActivity: `${faker.number.int({ min: 1, max: 24 })} hours ago`,
    proposal: faker.lorem.paragraphs(2),
    userOpinions: Array.from({ length: faker.number.int({ min: 1, max: 5 }) }, () => faker.lorem.sentence()), 
    originalContent: Array.from(
      { length: faker.number.int({ min: 1, max: 3 }) },
      (): {
        url: string;
        text: string;
      } => ({
        url: faker.internet.url(),
        text: faker.lorem.words(3),
      })
    ),
  };
};

export function makeData(...lens: number[]) {
  const makeDataLevel = (depth = 0): ForumPost[] => {
    const len = lens[depth]!;
    return range(len).map((d): ForumPost => {
      return {
        ...newForumPost(d),
      };
    });
  };

  return makeDataLevel();
}

const data = makeData(1000);

// Simulates a backend API
export const fetchData = async (start: number, size: number) => {
  const dbData = [...data];

  // Simulate a backend API
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    data: dbData.slice(start, start + size),
    meta: {
      totalRowCount: dbData.length,
    },
  };
};
