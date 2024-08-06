from typing import Dict, Any
import httpx
import asyncio
from op_forum_agg.db.models import AgoraProposal
import os

BASE_URL = "https://vote.optimism.io/api/v1/proposals"
BEARER_TOKEN = os.getenv("AGORA_BEARER_TOKEN")

if not BEARER_TOKEN:
    raise ValueError("AGORA_BEARER_TOKEN is not set.")


class AgoraProposalsService:
    @staticmethod
    async def fetch_proposals(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"Rate limited. Waiting for {retry_after} seconds.")
                await asyncio.sleep(retry_after)
                return await AgoraProposalsService.fetch_proposals(url, headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def acquire_and_save():
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Accept": "application/json",
        }

        all_proposals = []
        next_url = BASE_URL

        while next_url:
            print(f"Fetching: {next_url}")
            data = await AgoraProposalsService.fetch_proposals(next_url, headers)

            all_proposals.extend(data.get("data", []))

            metadata = data.get("meta", {})
            if metadata.get("has_next", False):
                next_url = f"{BASE_URL}?offset={metadata.get('next_offset', 0)}"
            else:
                next_url = None

        proposal_objects = []
        for proposal in all_proposals:
            proposal_objects.append(
                AgoraProposal(
                    externalId=proposal["id"],
                    proposer=proposal["proposer"],
                    snapshotBlockNumber=proposal["snapshotBlockNumber"],
                    createdTime=proposal["createdTime"],
                    startTime=proposal["startTime"],
                    endTime=proposal["endTime"],
                    cancelledTime=proposal.get("cancelledTime"),
                    executedTime=proposal.get("executedTime"),
                    markdownTitle=proposal["markdowntitle"],
                    description=proposal["description"],
                    quorum=proposal["quorum"],
                    approvalThreshold=proposal.get("approvalThreshold"),
                    proposalData=proposal["proposalData"],
                    unformattedProposalData=proposal["unformattedProposalData"],
                    proposalResults=proposal["proposalResults"],
                    proposalType=proposal["proposalType"],
                    status=proposal["status"],
                    createdTransactionHash=proposal.get("createdTransactionHash"),
                    cancelledTransactionHash=proposal.get("cancelledTransactionHash"),
                    executedTransactionHash=proposal.get("executedTransactionHash"),
                )
            )

        await AgoraProposal.bulk_create(
            proposal_objects,
            update_fields=[
                "proposer",
                "snapshotBlockNumber",
                "createdTime",
                "startTime",
                "endTime",
                "cancelledTime",
                "executedTime",
                "markdownTitle",
                "description",
                "quorum",
                "approvalThreshold",
                "proposalData",
                "unformattedProposalData",
                "proposalResults",
                "proposalType",
                "status",
                "createdTransactionHash",
                "cancelledTransactionHash",
                "executedTransactionHash",
            ],
            on_conflict=["externalId"],
        )

        print(f"Acquired and saved {len(proposal_objects)} Agora proposals")

    @staticmethod
    async def update_relationships():
        # If there are any relationships to update, implement them here
        pass
