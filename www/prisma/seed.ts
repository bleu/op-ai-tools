import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  // external ids which front-end will display filter options
  const defaultFilterableIds = ["41", "1", "69", "48", "46"];

  const updatePromises = defaultFilterableIds.map((id) =>
    prisma.forumPostCategory.update({
      where: { externalId: id },
      data: { filterable: true },
    })
  );

  await Promise.all(updatePromises);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
