import asyncio
import json
import logging
from typing import List, Dict
from op_data.db.models import SnapshotProposal, Topic
from op_data.utils.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

SNAPSHOT_HUB_URL = "https://hub.snapshot.org/graphql"
SPACE_IDS = ["citizenshouse.eth", "opcollective.eth"]


class SnapshotService(BaseScraper):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    async def fetch_proposals(self, query: str, skip: int) -> Dict:
        query_with_skip = query.replace("skip: 0", f"skip: {skip}")
        try:
            return await self.retry_request(
                "", method="POST", data={"query": query_with_skip}
            )
        except Exception as e:
            logger.error(f"An error occurred while fetching query data: {e}")
            raise

    async def get_all_proposals(self) -> List[Dict]:
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

        all_proposals = []
        skip = 0
        while True:
            proposals = await self.fetch_proposals(query, skip)
            all_proposals.extend(proposals.get("data", {}).get("proposals", []))

            if len(proposals.get("data", {}).get("proposals", [])) < 1000:
                break

            skip += 1000

        return all_proposals

    @classmethod
    async def acquire_and_save(cls):
        try:
            proposals = await cls(SNAPSHOT_HUB_URL).get_all_proposals()

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
                    if field != "id" and field != "Topic"
                ],
                on_conflict=["externalId"],
            )

            logger.info(
                f"Acquired and saved {len(snapshot_proposals)} snapshot proposals"
            )
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
                forum_posts = await Topic.filter(
                    url__in=[u["url"] for u in forum_post_updates]
                ).all()

                for forum_post in forum_posts:
                    update = next(
                        (u for u in forum_post_updates if u["url"] == forum_post.url),
                        None,
                    )
                    if update:
                        forum_post.snapshotProposal = update["snapshotProposal"]
                        forum_posts_to_update.append(forum_post)

            await asyncio.gather(
                *[forum_post.save() for forum_post in forum_posts_to_update]
            )

            logger.info(
                f"Updated {len(forum_posts_to_update)} forum posts with snapshot proposals"
            )
        except Exception as e:
            logger.error(f"Error updating relationships: {e}")
