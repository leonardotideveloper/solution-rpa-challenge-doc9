from .easy_service import execute as execute_easy
from .extreme_service import execute as execute_extreme
from .hard_service import execute as execute_hard
from .pow_service import solve_pow, solve_pow_parallel

__all__ = [
    "execute_easy",
    "execute_extreme",
    "execute_hard",
    "solve_pow",
    "solve_pow_parallel",
]
