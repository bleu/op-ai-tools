from typing import Dict, Any
import httpx
import asyncio
from op_forum_agg.db.models import AgoraProposal
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://vote.optimism.io/api/v1/proposals"
BEARER_TOKEN = os.getenv("AGORA_BEARER_TOKEN")

if not BEARER_TOKEN:
    raise ValueError("AGORA_BEARER_TOKEN is not set.")


import logging

logger = logging.getLogger(__name__)

class AgoraProposalsService:
    @staticmethod
    async def fetch_proposals(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited. Waiting for {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    return await AgoraProposalsService.fetch_proposals(url, headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e}")
                raise
            except Exception as e:
                logger.error(f"An error occurred while fetching proposals: {e}")
                raise

    @staticmethod
    async def acquire_and_save():
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Accept": "application/json",
        }

        all_proposals = []
        next_url = BASE_URL

        while next_url:
            logger.info(f"Fetching: {next_url}")
            try:
                data = await AgoraProposalsService.fetch_proposals(next_url, headers)
                all_proposals.extend(data.get("data", []))

                metadata = data.get("meta", {})
                if metadata.get("has_next", False):
                    next_url = f"{BASE_URL}?offset={metadata.get('next_offset', 0)}"
                else:
                    next_url = None
            except Exception as e:
                logger.error(f"Failed to fetch proposals: {e}")
                break

        proposal_objects = [
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
            for proposal in all_proposals
        ]

        try:
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
            logger.info(f"Acquired and saved {len(proposal_objects)} Agora proposals")
        except Exception as e:
            logger.error(f"Failed to save Agora proposals: {e}")

    @staticmethod
    async def update_relationships():
        # If there are any relationships to update, implement them here
        pass
