UPSERT_CATEGORIES = """
    INSERT INTO "ForumPostCategory" (external_id, name, color, slug, description, topic_url)
    VALUES (%s, %s, %s, %s, %s, %s)
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
        VALUES (%s, %s, %s, %s)
        ON CONFLICT ("external_id") DO UPDATE SET
        "url" = EXCLUDED."url",
        "type" = EXCLUDED."type",
        "rawData" = EXCLUDED."rawData"
    """

RETRIEVE_RAW_THREADS = """
    SELECT "external_id", "url", "type", "rawData"
    FROM "RawForumPost"
    WHERE "type" = 'thread'
"""


RETRIEVE_RAW_THREAD_BY_URL = """
    SELECT "external_id", "url", "type", "rawData"
    FROM "RawForumPost"
    WHERE "url" = %s
"""


LIST_CATEGORIES = """
    SELECT *
    FROM "ForumPostCategory"
"""


CREATE_FORUM_POSTS = """
    INSERT INTO "ForumPost" (
        "external_id", "url", "title", "username", "displayUsername", "category", 
        "about", "firstPost", "reaction", "overview", "tldr", "createdAt", "updatedAt"
    ) VALUES (
        %(external_id)s, %(url)s, %(title)s, %(username)s, %(displayUsername)s, %(category)s, 
        %(about)s, %(firstPost)s, %(reaction)s, %(overview)s, %(tldr)s, NOW(), NOW()
    )
    ON CONFLICT ("external_id") DO UPDATE SET
    "url" = EXCLUDED."url",
    "title" = EXCLUDED."title",
    "username" = EXCLUDED."username",
    "displayUsername" = EXCLUDED."displayUsername",
    "category" = EXCLUDED."category",
    "about" = EXCLUDED."about",
    "firstPost" = EXCLUDED."firstPost",
    "reaction" = EXCLUDED."reaction",
    "overview" = EXCLUDED."overview",
    "tldr" = EXCLUDED."tldr",
    "updatedAt" = NOW()
    """
