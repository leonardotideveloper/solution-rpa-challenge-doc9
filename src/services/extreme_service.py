import json

from src.config import get_logger, settings
from src.services.pow_service import solve_pow
from src.utils import (
    PowError,
    WebSocketError,
    aes_cbc_decrypt,
    connect_websocket,
    derive_key_sha256,
    post,
)

logger = get_logger()


async def execute() -> dict:
    logger.info("[extreme_service] Step 1: Initializing session...")
    init_resp = await post(
        f"{settings.base_url}/api/extreme/init",
        json_data={},
    )
    session_id = init_resp["session_id"]
    ws_ticket = init_resp["ws_ticket"]
    logger.info(f"[extreme_service] Session ID: {session_id}")

    logger.info("[extreme_service] Step 2: Connecting to WebSocket...")
    ws_url = f"wss://localhost:3000/ws?ticket={ws_ticket}&session_id={session_id}"

    async with await connect_websocket(ws_url) as ws:
        logger.info("[extreme_service] Step 3: Receiving PoW challenge...")
        pow_msg = await ws.recv()
        pow_data = json.loads(pow_msg)

        if pow_data.get("type") != "pow_challenge":
            raise PowError(f"Expected pow_challenge, got: {pow_data}")

        pow_challenge = pow_data["prefix"]
        difficulty = pow_data.get("difficulty", settings.pow_difficulty)
        logger.info(
            f"[extreme_service] Challenge: {pow_challenge[:32]}..., difficulty: {difficulty}"
        )

        logger.info("[extreme_service] Step 4: Solving PoW...")
        nonce, pow_hash = await solve_pow(pow_challenge, difficulty)
        logger.info(f"[extreme_service] Nonce: {nonce}, Hash: {pow_hash[:32]}...")

        logger.info("[extreme_service] Step 5: Sending PoW solution...")
        await ws.send(json.dumps({"nonce": str(nonce)}))

        logger.info("[extreme_service] Step 6: Receiving intermediate_token...")
        pow_result_msg = await ws.recv()
        pow_result = json.loads(pow_result_msg)

        if pow_result.get("type") != "pow_result":
            raise WebSocketError(f"Expected pow_result, got: {pow_result}")

        intermediate_token = pow_result["intermediate_token"]
        logger.info(
            f"[extreme_service] intermediate_token: {intermediate_token[:32]}..."
        )

    logger.info(
        "[extreme_service] Step 7: Verifying token and getting encrypted payload..."
    )
    verify_resp = await post(
        f"{settings.base_url}/api/extreme/verify-token",
        json_data={
            "session_id": session_id,
            "intermediate_token": intermediate_token,
        },
        referer=f"{settings.base_url}/extreme/",
    )

    encrypted_payload = verify_resp.get("token") or verify_resp.get("encrypted_payload")
    logger.info(f"[extreme_service] Encrypted payload: {encrypted_payload[:50]}...")

    logger.info("[extreme_service] Step 8: Decrypting payload to get OTP...")
    key = derive_key_sha256(session_id, settings.extreme_key_derivation_salt)
    payload = aes_cbc_decrypt(encrypted_payload, key)
    otp = payload["otp"]
    logger.info(f"[extreme_service] OTP: {otp}")

    logger.info("[extreme_service] Step 9: Submitting final authentication...")
    final_resp = await post(
        f"{settings.base_url}/api/extreme/complete",
        json_data={
            "session_id": session_id,
            "otp": otp,
            "username": settings.extreme_username,
            "password": settings.extreme_password,
        },
        referer=f"{settings.base_url}/extreme/",
    )

    logger.info("[extreme_service] Authentication completed successfully")
    return {
        "token": final_resp.get("token", ""),
        "proof_hash": final_resp.get("proof_hash", ""),
        "elapsed_server_ms": final_resp.get("elapsed_ms", 0),
    }
