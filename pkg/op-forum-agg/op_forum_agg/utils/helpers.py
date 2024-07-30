import httpx


async def fetch_info(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def snake_to_camel(dictionary):
    def convert_key(key):
        components = key.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    return {convert_key(key): value for key, value in dictionary.items()}
