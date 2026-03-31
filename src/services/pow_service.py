import multiprocessing
from typing import Tuple

from src.config import get_logger, settings
from src.utils import PowError, check_pow, sha256_hex

logger = get_logger()


def _solve_pow_chunk(args: Tuple[str, int, int, int]) -> Tuple[int, str]:
    challenge, difficulty, start, end = args
    for nonce in range(start, end):
        if check_pow(challenge, nonce, difficulty):
            h = sha256_hex(challenge + str(nonce))
            return nonce, h
    return -1, ""


def solve_pow_parallel(
    challenge: str,
    difficulty: int | None = None,
    num_workers: int | None = None,
) -> Tuple[int, str]:
    if difficulty is None:
        difficulty = settings.pow_difficulty
    if num_workers is None:
        num_workers = settings.pow_num_workers

    with multiprocessing.Pool(processes=num_workers) as pool:
        for start in range(0, settings.pow_max_nonce, settings.pow_chunk_size):
            end = min(start + settings.pow_chunk_size, settings.pow_max_nonce)
            args = (challenge, difficulty, start, end)

            result = pool.apply_async(_solve_pow_chunk, (args,))
            try:
                nonce, h = result.get(timeout=120)
                if nonce != -1:
                    return nonce, h
            except Exception as e:
                logger.warning(f"PoW chunk failed: {e}")

    raise PowError("PoW solution not found within range")


async def solve_pow(challenge: str, difficulty: int | None = None) -> Tuple[int, str]:
    logger.info(
        f"[pow_service] Solving PoW with difficulty={difficulty or settings.pow_difficulty}"
    )
    result = solve_pow_parallel(challenge, difficulty)
    logger.info(f"[pow_service] Solution found: nonce={result[0]}")
    return result
