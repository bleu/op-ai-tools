UPSERT_CATEGORIES = """
    INSERT INTO "ForumPostCategory" (external_id, name, color, slug, description, topic_url)
    VALUES %s
    ON CONFLICT (external_id)
    DO UPDATE SET
      name = EXCLUDED.name,
      color = EXCLUDED.color,
      slug = EXCLUDED.slug,
      description = EXCLUDED.description,
      topic_url = EXCLUDED.topic_url;
    """

UPSERT_THREADS = """
        INSERT INTO "RawForumPost" ("external_id", "url", "type", "rawData")
        VALUES %s
        ON CONFLICT ("external_id") DO UPDATE SET
        "url" = EXCLUDED."url",
        "type" = EXCLUDED."type",
        "rawData" = EXCLUDED."rawData"
    """
