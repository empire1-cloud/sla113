"""Managed receipt signing. Production refuses to use an application secret."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import os
from dataclasses import dataclass
from typing import Protocol


class SigningConfigurationError(RuntimeError):
    pass


class ReceiptSigner(Protocol):
    key_id: str
    algorithm: str

    async def sign_digest(self, digest_hex: str) -> str: ...
    async def verify_digest(self, digest_hex: str, signature_b64: str) -> bool: ...


@dataclass
class DevelopmentHmacSigner:
    """Test/development signer. It is deliberately rejected in production."""

    key: bytes
    key_id: str = "development-only"
    algorithm: str = "HMAC-SHA256-DEVELOPMENT-ONLY"

    async def sign_digest(self, digest_hex: str) -> str:
        return base64.urlsafe_b64encode(
            hmac.new(self.key, digest_hex.encode("ascii"), hashlib.sha256).digest()
        ).decode("ascii").rstrip("=")

    async def verify_digest(self, digest_hex: str, signature_b64: str) -> bool:
        return hmac.compare_digest(await self.sign_digest(digest_hex), signature_b64)


class GoogleCloudKmsSigner:
    """Asymmetric signer backed by a Google Cloud KMS CryptoKeyVersion."""

    algorithm = "GOOGLE-CLOUD-KMS-ASYMMETRIC-SHA256"

    def __init__(self, key_version_name: str) -> None:
        if "/cryptoKeyVersions/" not in key_version_name:
            raise SigningConfigurationError("A full KMS CryptoKeyVersion resource name is required")
        self.key_version_name = key_version_name
        self.key_id = key_version_name

    @staticmethod
    def _client():
        try:
            from google.cloud import kms_v1
        except ImportError as exc:
            raise SigningConfigurationError("google-cloud-kms is required for production receipt signing") from exc
        return kms_v1.KeyManagementServiceClient(), kms_v1

    def _sign_sync(self, digest_hex: str) -> str:
        client, kms_v1 = self._client()
        response = client.asymmetric_sign(
            request={
                "name": self.key_version_name,
                "digest": kms_v1.Digest(sha256=bytes.fromhex(digest_hex)),
            }
        )
        return base64.urlsafe_b64encode(response.signature).decode("ascii").rstrip("=")

    async def sign_digest(self, digest_hex: str) -> str:
        return await asyncio.to_thread(self._sign_sync, digest_hex)

    def _verify_sync(self, digest_hex: str, signature_b64: str) -> bool:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec, padding, utils
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        client, _ = self._client()
        pem = client.get_public_key(request={"name": self.key_version_name}).pem.encode("ascii")
        key = load_pem_public_key(pem)
        signature = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
        try:
            if hasattr(key, "curve"):
                key.verify(signature, bytes.fromhex(digest_hex), ec.ECDSA(utils.Prehashed(hashes.SHA256())))
            else:
                key.verify(signature, bytes.fromhex(digest_hex), padding.PKCS1v15(), utils.Prehashed(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False

    async def verify_digest(self, digest_hex: str, signature_b64: str) -> bool:
        return await asyncio.to_thread(self._verify_sync, digest_hex, signature_b64)


def signer_from_environment() -> ReceiptSigner:
    kms_key = os.getenv("ECONOMIC_TRUTH_KMS_KEY_VERSION", "").strip()
    if kms_key:
        return GoogleCloudKmsSigner(kms_key)

    environment = os.getenv("ENVIRONMENT", os.getenv("NODE_ENV", "development")).lower()
    if environment in {"test", "development", "dev", "local"}:
        dev_key = os.getenv("ECONOMIC_TRUTH_DEV_SIGNING_KEY", "").encode("utf-8")
        if len(dev_key) < 32:
            raise SigningConfigurationError(
                "Set a 32+ byte ECONOMIC_TRUTH_DEV_SIGNING_KEY for local use; no fallback key exists"
            )
        return DevelopmentHmacSigner(dev_key)

    raise SigningConfigurationError(
        "Production requires ECONOMIC_TRUTH_KMS_KEY_VERSION; application-secret receipt signing is refused"
    )
