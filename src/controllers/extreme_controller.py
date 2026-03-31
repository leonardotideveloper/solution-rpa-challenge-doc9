import time

from src.config import get_logger
from src.services import execute_extreme

logger = get_logger()


class ExtremeController:
    name = "extreme"

    async def run(self) -> dict:
        start_time = time.time()
        logger.info("[extreme_controller] Starting...")

        try:
            result = await execute_extreme()
            result["success"] = True
            logger.info("[extreme_controller] Completed successfully")
        except Exception as e:
            logger.error(f"[extreme_controller] Failed: {e}")
            result = {"success": False, "error": str(e)}

        result["elapsed_ms"] = int((time.time() - start_time) * 1000)
        return result


async def run_extreme_controller() -> dict:
    controller = ExtremeController()
    return await controller.run()
