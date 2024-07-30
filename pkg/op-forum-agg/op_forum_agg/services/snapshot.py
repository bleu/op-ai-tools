import json
from typing import List, Dict
import httpx
from op_forum_agg.db.models import SnapshotProposal, ForumPost

SNAPSHOT_HUB_URL = "https://hub.snapshot.org/graphql"
SPACE_IDS = ["citizenshouse.eth", "opcollective.eth"]


class SnapshotService:
    @staticmethod
    async def get_query_data(query: str, skip: int) -> List[Dict]:
        query_with_skip = query.replace("skip: 0", f"skip: {skip}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SNAPSHOT_HUB_URL, json={"query": query_with_skip}
            )
        response.raise_for_status()
        result = response.json()
        return result["data"]["proposals"]

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
            print(
                f"Fetching data with skip {skip}, page size {page_size}, pages per group {pages_per_group}, max pages {max_pages}"
            )
            tasks = []
            for i in range(pages_per_group):
                current_skip = skip + page_size * i
                if current_skip >= max_skip:
                    current_skip = max_skip
                items = await SnapshotService.get_query_data(query, current_skip)
                tasks.append(items)

            for items in tasks:
                data.extend(items)
                if len(items) < page_size:
                    break

            print(f"Total items: {len(data)}")
            skip += page_size * pages_per_group
            print(f"Skip: {skip}, max skip: {max_skip}, tasks: {len(tasks)}")
            if len(tasks) == 0 or len(tasks[-1]) < page_size:
                break

        return data

    @staticmethod
    async def sync_proposals():
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

        proposals = await SnapshotService.get_paginated_data(query)

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

            snapshot_proposal, created = await SnapshotProposal.update_or_create(
                externalId=proposal_data["externalId"], defaults=proposal_data
            )

            if proposal_data["discussion"]:
                forum_post = await ForumPost.get_or_none(
                    url=proposal_data["discussion"]
                )
                if forum_post:
                    forum_post.snapshotProposal = snapshot_proposal
                    await forum_post.save()

        print("Proposals synced successfully")
