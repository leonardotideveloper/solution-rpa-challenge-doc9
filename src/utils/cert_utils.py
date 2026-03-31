import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    pkcs12,
)


def extract_pem_from_pfx(pfx_path: str, password: str) -> tuple[bytes, bytes]:
    with open(pfx_path, "rb") as f:
        pfx_data = f.read()

    private_key, certificate, _ = pkcs12.load_key_and_certificates(
        pfx_data, password.encode()
    )

    cert_pem = certificate.public_bytes(Encoding.PEM)
    key_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption(),
    )

    return cert_pem, key_pem


def create_temp_cert_files(cert_pem: bytes, key_pem: bytes) -> tuple[str, str]:
    with tempfile.NamedTemporaryFile(
        mode="wb", suffix=".pem", delete=False
    ) as cert_file:
        cert_file.write(cert_pem)
        cert_path = cert_file.name

    with tempfile.NamedTemporaryFile(
        mode="wb", suffix=".key", delete=False
    ) as key_file:
        key_file.write(key_pem)
        key_path = key_file.name

    return cert_path, key_path


def cleanup_temp_files(*paths: str) -> None:
    for path in paths:
        Path(path).unlink(missing_ok=True)
