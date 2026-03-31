from src.config import get_logger, settings
from src.utils import ApiError, post

logger = get_logger()


async def execute() -> dict:
    logger.info("[easy_service] Executing login...")

    data = await post(
        f"{settings.base_url}/api/easy/login",
        json_data={
            "username": settings.easy_username,
            "password": settings.easy_password,
        },
        referer=f"{settings.base_url}/easy/",
    )

    if not data.get("success"):
        raise ApiError(f"Login failed: {data.get('message')}")

    logger.info("[easy_service] Login successful")
    return {
        "token": data.get("token", ""),
        "message": data.get("message", ""),
    }
