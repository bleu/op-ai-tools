import os
from datetime import datetime
import json
import requests

SNAPSHOT_HUB_URL = "https://hub.snapshot.org/graphql"
SPACE_IDS = ["citizenshouse.eth", "opcollective.eth"]


def get_query_data(query, skip):
    query_with_skip = query.replace("skip: 0", f"skip: {skip}")
    response = requests.post(SNAPSHOT_HUB_URL, json={"query": query_with_skip})
    response.raise_for_status()
    result = response.json()
    return result["data"]["proposals"]


def get_paginated_data(query, page_size=1000, pages_per_group=1, max_pages=1000):
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
            items = get_query_data(query, current_skip)
            tasks.append(items)

        for items in tasks:
            data += items
            if len(items) < page_size:
                break

        print(f"Total items: {len(data)}")
        skip += page_size * pages_per_group
        print(f"Skip: {skip}, max skip: {max_skip}, tasks: {len(tasks)}")
        if len(tasks) == 0 or len(tasks[-1]) < page_size:
            break

    return data


def download_proposals():
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

    proposals = get_paginated_data(query)

    today_yyyymmdd = datetime.now().strftime("%Y%m%d")
    dataset_dir = f"../../data/003-snapshot-spaces-proposals-{today_yyyymmdd}"
    os.makedirs(dataset_dir, exist_ok=True)
    with open(
        f"../../data/003-snapshot-spaces-proposals-{today_yyyymmdd}/dataset.jsonl", "w"
    ) as f:
        for proposal in proposals:
            proposal_data = {
                "id": proposal["id"],
                "space_id": proposal["space"]["id"],
                "space_name": proposal["space"]["name"],
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
                "quorum_type": proposal["quorumType"],
                "snapshot": proposal["snapshot"],
                "scores": proposal["scores"],
            }

            if proposal["state"] == "closed":
                winner = proposal["scores"].index(max(proposal["scores"]))
                proposal_data["winning_option"] = proposal["choices"][winner]
            else:
                proposal_data["winning_option"] = None

            f.write(json.dumps(proposal_data) + "\n")

    print("Proposals saved to proposals.jsonl")


if __name__ == "__main__":
    download_proposals()
