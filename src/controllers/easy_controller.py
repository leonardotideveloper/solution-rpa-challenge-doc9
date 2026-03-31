import time

from src.config import get_logger
from src.services import execute_easy

logger = get_logger()


class EasyController:
    name = "easy"

    async def run(self) -> dict:
        start_time = time.time()
        logger.info("[easy_controller] Starting...")

        try:
            result = await execute_easy()
            result["success"] = True
            logger.info("[easy_controller] Completed successfully")
        except Exception as e:
            logger.error(f"[easy_controller] Failed: {e}")
            result = {"success": False, "error": str(e)}

        result["elapsed_ms"] = int((time.time() - start_time) * 1000)
        return result


async def run_easy_controller() -> dict:
    controller = EasyController()
    return await controller.run()
