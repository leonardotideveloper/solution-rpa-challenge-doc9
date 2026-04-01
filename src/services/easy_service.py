from src.config import get_logger, settings
from src.models import EasyLoginResponse
from src.utils import ApiError, post

logger = get_logger()


async def execute() -> dict:
    logger.info("[easy_service] Executing login...")

    raw_data = await post(
        f"{settings.base_url}/api/easy/login",
        json_data={
            "username": settings.easy_username,
            "password": settings.easy_password,
        },
        referer=f"{settings.base_url}/easy/",
    )

    data = EasyLoginResponse(**raw_data)
    if not data.success:
        raise ApiError(f"Login failed: {data.message}")

    logger.info("[easy_service] Login successful")
    return {
        "token": data.token or "",
        "message": data.message or "",
    }
