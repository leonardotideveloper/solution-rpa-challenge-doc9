from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    base_url: str = "https://localhost:3000"
    hard_second_stage_url: str = "https://localhost:3001"

    timeout_seconds: int = 30

    easy_username: str = ""
    easy_password: str = ""

    hard_username: str = ""
    hard_password: str = ""

    extreme_username: str = ""
    extreme_password: str = ""

    pow_difficulty: int = 5
    pow_max_nonce: int = 50_000_000
    pow_chunk_size: int = 50_000
    pow_num_workers: int = 16

    extreme_key_derivation_salt: str = "extreme_secret_key"
    hard_challenge_secret: str = "rpa_hard_challenge_2026"

    cert_password: str = "test123"

    @property
    def cert_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent / "certs"

    @property
    def cert_client_pfx(self) -> Path:
        return self.cert_dir / "client.pfx"

    @property
    def cert_ca_crt(self) -> Path:
        return self.cert_dir / "ca.crt"


settings = Settings()
