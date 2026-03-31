import httpx
from playwright.async_api import async_playwright

from src.config import get_logger, settings
from src.utils import (
    ApiError,
    BotError,
    cleanup_temp_files,
    create_temp_cert_files,
    extract_pem_from_pfx,
    post,
)

logger = get_logger()


async def execute() -> dict:
    logger.info("[hard_service] Step 1: Launching headless browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            accept_downloads=False,
            ignore_https_errors=True,
        )
        page = await context.new_page()

        logger.info("[hard_service] Step 2: Navigating to /hard/")
        await page.goto(f"{settings.base_url}/hard/")

        logger.info("[hard_service] Step 3: Extracting challenge values from page...")
        challenge_value = await page.locator("#challenge").input_value()
        timestamp_value = await page.locator("#timestamp").input_value()
        nonce_value = await page.locator("#nonce").input_value()

        if not all([challenge_value, timestamp_value, nonce_value]):
            raise BotError("Failed to extract challenge values from page")

        logger.info(f"[hard_service] Challenge: {challenge_value[:32]}...")
        logger.info(f"[hard_service] Timestamp: {timestamp_value}")
        logger.info(f"[hard_service] Nonce: {nonce_value}")

        logger.info(
            "[hard_service] Step 4: Submitting credentials to /api/hard/login..."
        )

        login_data = await post(
            f"{settings.base_url}/api/hard/login",
            json_data={
                "username": settings.hard_username,
                "password": settings.hard_password,
                "challenge": challenge_value,
                "timestamp": timestamp_value,
                "nonce": nonce_value,
            },
            referer=f"{settings.base_url}/hard/",
        )

        if not login_data.get("success"):
            raise ApiError(f"Login failed: {login_data.get('message')}")

        redirect_url = login_data.get("redirect")
        ttl_seconds = login_data.get("ttl_seconds", 30)
        logger.info(f"[hard_service] Login successful, redirect: {redirect_url}")
        logger.info(f"[hard_service] TTL: {ttl_seconds}s")

        await context.close()
        await browser.close()

        logger.info("[hard_service] Step 5: Following redirect to port 3001 (mTLS)...")
        token = await _handle_mtls(redirect_url)

        logger.info("[hard_service] mTLS authentication successful")
        return {
            "token": token,
            "message": login_data.get("message", ""),
        }


async def _handle_mtls(redirect_url: str) -> str:
    logger.info("[hard_service] Step 6: Making mTLS request to port 3001...")
    cert_pem, key_pem = extract_pem_from_pfx(
        str(settings.cert_client_pfx), settings.cert_password
    )
    cert_path, key_path = create_temp_cert_files(cert_pem, key_pem)

    try:
        async with httpx.AsyncClient(
            verify=False, cert=(cert_path, key_path)
        ) as client:
            response = await client.get(
                redirect_url,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    ),
                },
            )

        logger.info(f"[hard_service] Response status: {response.status_code}")
        if response.status_code >= 400:
            raise ApiError(
                f"mTLS request failed: {response.status_code}",
                status_code=response.status_code,
            )

    finally:
        cleanup_temp_files(cert_path, key_path)

    return redirect_url.split("token=")[-1] if "token=" in redirect_url else ""
