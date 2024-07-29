UPSERT_CATEGORIES = """
    INSERT INTO "ForumPostCategory" ("externalId", "name", "color", "slug", "description", "topicUrl")
    VALUES (%(external_id)s, %(name)s, %(color)s, %(slug)s, %(description)s, %(topic_url)s)
    ON CONFLICT ("externalId")
    DO UPDATE SET
      "name" = EXCLUDED."name",
      "color" = EXCLUDED."color",
      "slug" = EXCLUDED."slug",
      "description" = EXCLUDED."description",
      "topicUrl" = EXCLUDED."topicUrl";
    """

UPSERT_THREADS = """
    INSERT INTO "RawForumPost" ("externalId", "url", "type", "rawData")
    VALUES (%(external_id)s, %(url)s, %(type)s, %(raw_data)s)
    ON CONFLICT ("externalId") DO UPDATE SET
    "url" = EXCLUDED."url",
    "type" = EXCLUDED."type",
    "rawData" = EXCLUDED."rawData"
"""


RETRIEVE_RAW_THREADS = """
    SELECT "externalId", "url", "type", "rawData"
    FROM "RawForumPost"
    WHERE "type" = 'thread'
"""


RETRIEVE_RAW_THREAD_BY_URL = """
    SELECT "externalId", "url", "type", "rawData", "id"
    FROM "RawForumPost"
    WHERE "url" = %s
"""


LIST_CATEGORIES = """
    SELECT *
    FROM "ForumPostCategory"
"""


CREATE_FORUM_POSTS = """
    INSERT INTO "ForumPost" (
        "externalId", "url", "title", "username", "displayUsername", "categoryId", 
        "about", "firstPost", "reaction", "overview", "tldr", "rawForumPostId", 
        "classification", "lastActivity", "readTime", "createdAt", "updatedAt"
    ) VALUES (
        %(external_id)s, %(url)s, %(title)s, %(username)s, %(display_username)s, %(category_id)s, 
        %(about)s, %(first_post)s, %(reaction)s, %(overview)s, %(tldr)s, %(raw_forum_post_id)s,
        %(classification)s, %(last_activity)s, %(read_time)s, %(created_at)s, NOW()
    )
    ON CONFLICT ("externalId") DO UPDATE SET
    "url" = EXCLUDED."url",
    "title" = EXCLUDED."title",
    "username" = EXCLUDED."username",
    "displayUsername" = EXCLUDED."displayUsername",
    "categoryId" = EXCLUDED."categoryId",
    "about" = EXCLUDED."about",
    "firstPost" = EXCLUDED."firstPost",
    "reaction" = EXCLUDED."reaction",
    "overview" = EXCLUDED."overview",
    "tldr" = EXCLUDED."tldr",
    "rawForumPostId" = EXCLUDED."rawForumPostId",
    "classification" = EXCLUDED."classification",
    "lastActivity" = EXCLUDED."lastActivity",
    "readTime" = EXCLUDED."readTime",
    "updatedAt" = NOW()
    """
