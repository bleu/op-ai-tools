import logging
from typing import Dict, Any, List
from op_data.db.models import AgoraProposal
import os
from op_data.utils.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AgoraProposalService(BaseScraper):
    def __init__(self, base_url: str, bearer_token: str):
        super().__init__(base_url)
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/json",
        }

    async def fetch_proposals(self, offset: int = 0) -> Dict[str, Any]:
        endpoint = f"?offset={offset}" if offset else ""
        return await self.retry_request(endpoint, method="GET", headers=self.headers)

    async def fetch_all_proposals(self) -> List[Dict[str, Any]]:
        all_proposals = []
        offset = 0

        while True:
            logger.info(f"Fetching proposals with offset: {offset}")
            try:
                data = await self.fetch_proposals(offset)
                proposals = data.get("data", [])
                all_proposals.extend(proposals)

                metadata = data.get("meta", {})
                if metadata.get("has_next", False):
                    offset = metadata.get("next_offset", 0)
                else:
                    break
            except Exception as e:
                logger.error(f"Failed to fetch proposals: {e}")
                break

        return all_proposals

    @classmethod
    async def acquire_and_save(cls):
        base_url = "https://vote.optimism.io/api/v1/proposals"
        bearer_token = os.getenv("AGORA_BEARER_TOKEN")

        if not bearer_token:
            raise ValueError("AGORA_BEARER_TOKEN is not set.")

        all_proposals = await cls(base_url, bearer_token).fetch_all_proposals()

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
