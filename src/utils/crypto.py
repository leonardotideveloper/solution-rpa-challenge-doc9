import hashlib
import json

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from src.utils.exceptions import CryptoError


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def derive_key_sha256(session_id: str, salt: str) -> bytes:
    data = session_id + salt
    return hashlib.sha256(data.encode()).digest()


def hex_to_bytes(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)


def aes_cbc_decrypt(encrypted_data: str, key: bytes) -> dict:
    parts = encrypted_data.split(":")
    if len(parts) != 2:
        raise CryptoError(f"Expected 'iv:ciphertext' format, got {encrypted_data}")

    iv_hex, ciphertext_hex = parts
    iv = hex_to_bytes(iv_hex)
    ciphertext = hex_to_bytes(ciphertext_hex)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

    return json.loads(decrypted.decode("utf-8"))


def check_pow(challenge: str, nonce: int, difficulty: int) -> bool:
    h = sha256_hex(challenge + str(nonce))
    return h.startswith("0" * difficulty)
