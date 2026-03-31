"""
RPA Challenge Runner - Easy, Hard, and Extreme Controllers
"""

import asyncio
import sys

from src.config import setup_logging
from src.controllers import (
    EasyController,
    ExtremeController,
    HardController,
)


async def run_easy() -> dict:
    print("=" * 60)
    print("  RPA Challenge - Easy Level")
    print("=" * 60)

    controller = EasyController()
    result = await controller.run()

    print("\n" + "=" * 60)
    if result.get("success"):
        print("  RESULT: SUCCESS")
        print(f"  Token: {result.get('token', 'N/A')[:40]}...")
        print(f"  Message: {result.get('message', 'N/A')}")
    else:
        print("  RESULT: FAILED")
        print(f"  Error: {result.get('error', 'Unknown')}")
    print(f"  Time: {result.get('elapsed_ms', 0)}ms")
    print("=" * 60)

    return result


async def run_hard() -> dict:
    print("=" * 60)
    print("  RPA Challenge - Hard Level")
    print("=" * 60)

    controller = HardController()
    result = await controller.run()

    print("\n" + "=" * 60)
    if result.get("success"):
        print("  RESULT: SUCCESS")
        print(f"  Token: {result.get('token', 'N/A')[:40]}...")
        print(f"  Message: {result.get('message', 'N/A')}")
    else:
        print("  RESULT: FAILED")
        print(f"  Error: {result.get('error', 'Unknown')}")
    print(f"  Time: {result.get('elapsed_ms', 0)}ms")
    print("=" * 60)

    return result


async def run_extreme() -> dict:
    print("=" * 60)
    print("  RPA Challenge - Extreme Level")
    print("=" * 60)

    controller = ExtremeController()
    result = await controller.run()

    print("\n" + "=" * 60)
    if result.get("success"):
        print("  RESULT: SUCCESS")
        print(f"  Token: {result.get('token', 'N/A')[:40]}...")
        print(f"  Proof Hash: {result.get('proof_hash', 'N/A')}")
    else:
        print("  RESULT: FAILED")
        print(f"  Error: {result.get('error', 'Unknown')}")
    print(f"  Time: {result.get('elapsed_ms', 0)}ms")
    print("=" * 60)

    return result


def main() -> int:
    setup_logging()

    level = sys.argv[1].lower() if len(sys.argv) > 1 else "easy"

    try:
        if level == "easy":
            result = asyncio.run(run_easy())
        elif level == "hard":
            result = asyncio.run(run_hard())
        elif level == "extreme":
            result = asyncio.run(run_extreme())
        elif level == "all":
            results = {}
            results["easy"] = asyncio.run(run_easy())
            print("\n\n")
            results["hard"] = asyncio.run(run_hard())
            print("\n\n")
            results["extreme"] = asyncio.run(run_extreme())
            print("\n\n")
            print("=" * 60)
            print("  SUMMARY")
            print("=" * 60)
            for name, r in results.items():
                status = "PASS" if r.get("success") else "FAIL"
                print(f"  [{status}] {name}: {r.get('elapsed_ms', 0)}ms")
            result = results.get("easy")
        else:
            print(f"Unknown level: {level}")
            print("Usage: python run_bots.py [easy|hard|extreme|all]")
            return 1

        return 0 if result.get("success") else 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 130
    except Exception as e:
        print(f"\nFatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
