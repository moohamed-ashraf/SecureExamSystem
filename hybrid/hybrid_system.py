"""Hybrid RSA + AES cryptosystem."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any

from aes.aes_main import AES
from rsa.rsa_main import RSA


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def base64_to_bytes(encoded: str) -> bytes:
    return base64.b64decode(encoded.encode("ascii"))


def bytes_to_hex(data: bytes) -> str:
    return data.hex()


def text_to_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def bytes_to_text(data: bytes) -> str:
    return data.decode("utf-8")


@dataclass
class EncryptedPackage:
    student_id: str
    filename: str
    encrypted_aes_key_b64: str
    iv_b64: str
    ciphertext_b64: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "student_id": self.student_id,
            "filename": self.filename,
            "encrypted_aes_key_b64": self.encrypted_aes_key_b64,
            "iv_b64": self.iv_b64,
            "ciphertext_b64": self.ciphertext_b64,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EncryptedPackage":
        return cls(
            student_id=data["student_id"],
            filename=data["filename"],
            encrypted_aes_key_b64=data["encrypted_aes_key_b64"],
            iv_b64=data["iv_b64"],
            ciphertext_b64=data["ciphertext_b64"],
        )

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "EncryptedPackage":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


class HybridCryptosystem:
    @staticmethod
    def encrypt_submission(
        plaintext: bytes,
        student_id: str,
        filename: str,
        instructor_public_key: RSA,
    ) -> EncryptedPackage:
        aes_key = AES.generate_key()
        aes = AES(aes_key)
        iv, ciphertext = aes.encrypt_cbc(plaintext)
        encrypted_aes_key = instructor_public_key.encrypt(aes_key)

        return EncryptedPackage(
            student_id=student_id,
            filename=filename,
            encrypted_aes_key_b64=bytes_to_base64(encrypted_aes_key),
            iv_b64=bytes_to_base64(iv),
            ciphertext_b64=bytes_to_base64(ciphertext),
        )

    @staticmethod
    def encrypt_text_submission(
        text: str,
        student_id: str,
        filename: str,
        instructor_public_key: RSA,
    ) -> EncryptedPackage:
        return HybridCryptosystem.encrypt_submission(
            text_to_bytes(text), student_id, filename, instructor_public_key
        )

    @staticmethod
    def decrypt_submission(
        package: EncryptedPackage,
        instructor_private_key: RSA,
    ) -> bytes:
        encrypted_aes_key = base64_to_bytes(package.encrypted_aes_key_b64)
        iv = base64_to_bytes(package.iv_b64)
        ciphertext = base64_to_bytes(package.ciphertext_b64)

        aes_key = instructor_private_key.decrypt(encrypted_aes_key)
        aes = AES(aes_key)
        return aes.decrypt_cbc(ciphertext, iv)

    @staticmethod
    def decrypt_text_submission(
        package: EncryptedPackage,
        instructor_private_key: RSA,
    ) -> str:
        return bytes_to_text(
            HybridCryptosystem.decrypt_submission(package, instructor_private_key)
        )

    @staticmethod
    def encrypt_file(
        input_path: str,
        output_path: str,
        student_id: str,
        instructor_public_key: RSA,
    ) -> EncryptedPackage:
        with open(input_path, "rb") as f:
            plaintext = f.read()
        filename = os.path.basename(input_path)
        package = HybridCryptosystem.encrypt_submission(
            plaintext, student_id, filename, instructor_public_key
        )
        package.save(output_path)
        return package

    @staticmethod
    def decrypt_file(
        package_path: str,
        output_path: str,
        instructor_private_key: RSA,
    ) -> bytes:
        package = EncryptedPackage.load(package_path)
        plaintext = HybridCryptosystem.decrypt_submission(package, instructor_private_key)
        with open(output_path, "wb") as f:
            f.write(plaintext)
        return plaintext
