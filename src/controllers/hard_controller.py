import time

from src.config import get_logger
from src.services import execute_hard

logger = get_logger()


class HardController:
    name = "hard"

    async def run(self) -> dict:
        start_time = time.time()
        logger.info("[hard_controller] Starting...")

        try:
            result = await execute_hard()
            result["success"] = True
            logger.info("[hard_controller] Completed successfully")
        except Exception as e:
            logger.error(f"[hard_controller] Failed: {e}")
            result = {"success": False, "error": str(e)}

        result["elapsed_ms"] = int((time.time() - start_time) * 1000)
        return result


async def run_hard_controller() -> dict:
    controller = HardController()
    return await controller.run()
