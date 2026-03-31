import httpx


def get_default_headers() -> dict:
    return {
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        ),
        "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }


async def post(
    url: str,
    json_data: dict,
    origin: str = "https://localhost:3000",
    referer: str = "",
) -> dict:
    headers = get_default_headers()
    headers["Origin"] = origin
    headers["Content-Type"] = "application/json"
    if referer:
        headers["Referer"] = referer

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(url, json=json_data, headers=headers)
        response.raise_for_status()
        return response.json()
