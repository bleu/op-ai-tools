from typing import Dict
from op_data.db.models import Topic


async def classify_question(question_result: Dict) -> []:
    urls = question_result["data"].get("url_supporting", [])
    if not urls:
        return []

    topics = await Topic.filter(url__in=urls).prefetch_related("category")

    slugs = [topic.category.slug for topic in topics if topic.category is not None]

    return slugs
