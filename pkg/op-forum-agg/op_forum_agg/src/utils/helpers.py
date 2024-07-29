import httpx


def fetch_info(url: str):
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()
