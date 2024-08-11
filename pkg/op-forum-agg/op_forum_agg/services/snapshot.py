import asyncio
import json
from typing import List, Dict
import httpx
from op_forum_agg.db.models import SnapshotProposal, ForumPost

SNAPSHOT_HUB_URL = "https://hub.snapshot.org/graphql"
SPACE_IDS = ["citizenshouse.eth", "opcollective.eth"]


import logging

logger = logging.getLogger(__name__)

class SnapshotService:
    @staticmethod
    async def get_query_data(query: str, skip: int) -> List[Dict]:
        query_with_skip = query.replace("skip: 0", f"skip: {skip}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    SNAPSHOT_HUB_URL, json={"query": query_with_skip}
                )
            response.raise_for_status()
            result = response.json()
            return result["data"]["proposals"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while fetching query data: {e}")
            raise

    @staticmethod
    async def get_paginated_data(
        query: str,
        page_size: int = 1000,
        pages_per_group: int = 1,
        max_pages: int = 1000,
    ) -> List[Dict]:
        data = []
        skip = 0
        max_skip = 100_000_000

        while True:
            logger.info(
                f"Fetching data with skip {skip}, page size {page_size}, pages per group {pages_per_group}, max pages {max_pages}"
            )
            tasks = []
            for i in range(pages_per_group):
                current_skip = min(skip + page_size * i, max_skip)
                tasks.append(SnapshotService.get_query_data(query, current_skip))

            try:
                results = await asyncio.gather(*tasks)
                for items in results:
                    data.extend(items)
                    if len(items) < page_size:
                        break
            except Exception as e:
                logger.error(f"Error fetching paginated data: {e}")
                break

            logger.info(f"Total items: {len(data)}")
            skip += page_size * pages_per_group
            logger.debug(f"Skip: {skip}, max skip: {max_skip}, tasks: {len(tasks)}")
            if len(tasks) == 0 or len(results[-1]) < page_size:
                break

        return data

    @staticmethod
    async def acquire_and_save():
        query = f"""
            query {{
                proposals(first: 1000, skip: 0, where: {{space_in: {json.dumps(SPACE_IDS)}}}, orderBy: "created", orderDirection: desc) {{
                    id
                    space {{
                        id
                        name
                    }}
                    title
                    author
                    choices
                    state
                    votes
                    end
                    start
                    type
                    body
                    discussion
                    quorum
                    quorumType
                    snapshot
                    scores
                }}
            }}
        """

        try:
            proposals = await SnapshotService.get_query_data(query, 0)

            snapshot_proposals = []
            for proposal in proposals:
                proposal_data = {
                    "externalId": proposal["id"],
                    "spaceId": proposal["space"]["id"],
                    "spaceName": proposal["space"]["name"],
                    "title": proposal["title"],
                    "author": proposal["author"],
                    "choices": proposal["choices"],
                    "state": proposal["state"],
                    "votes": proposal["votes"],
                    "end": proposal["end"],
                    "start": proposal["start"],
                    "type": proposal["type"],
                    "body": proposal["body"],
                    "discussion": proposal["discussion"],
                    "quorum": proposal["quorum"],
                    "quorumType": proposal["quorumType"],
                    "snapshot": proposal["snapshot"],
                    "scores": proposal["scores"],
                }

                if proposal["state"] == "closed":
                    winner = proposal["scores"].index(max(proposal["scores"]))
                    proposal_data["winningOption"] = proposal["choices"][winner]

                snapshot_proposals.append(SnapshotProposal(**proposal_data))

            await SnapshotProposal.bulk_create(
                snapshot_proposals,
                update_fields=[
                    field
                    for field in SnapshotProposal._meta.fields
                    if field != "id" and field != "forumPost"
                ],
                on_conflict=["externalId"],
            )

            logger.info(f"Acquired and saved {len(snapshot_proposals)} snapshot proposals")
        except Exception as e:
            logger.error(f"Error acquiring and saving snapshot proposals: {e}")

    @staticmethod
    async def update_relationships():
        try:
            snapshot_proposals = await SnapshotProposal.filter(
                discussion__isnull=False
            ).all()
            forum_post_updates = [
                {
                    "url": proposal.discussion,
                    "snapshotProposal": proposal,
                }
                for proposal in snapshot_proposals
            ]

            forum_posts_to_update = []
            if forum_post_updates:
                forum_posts = await ForumPost.filter(
                    url__in=[u["url"] for u in forum_post_updates]
                ).all()

                for forum_post in forum_posts:
                    update = next(
                        (u for u in forum_post_updates if u["url"] == forum_post.url), None
                    )
                    if update:
                        forum_post.snapshotProposal = update["snapshotProposal"]
                        forum_posts_to_update.append(forum_post)

            await asyncio.gather(
                *[forum_post.save() for forum_post in forum_posts_to_update]
            )

            logger.info(f"Updated {len(forum_posts_to_update)} forum posts with snapshot proposals")
        except Exception as e:
            logger.error(f"Error updating relationships: {e}")
