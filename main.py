"""Entry point for SecureExamSystem."""

from __future__ import annotations

import argparse
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.chdir(_ROOT)

from aes.aes_main import AES
from hybrid.hybrid_system import HybridCryptosystem, bytes_to_hex
from rsa.mod_exp import mod_exp
from rsa.rsa_main import RSA
from ui.app import run_ui


def demo_console() -> None:
    print("=" * 60)
    print("SecureExamSystem — Console Demo")
    print("=" * 60)

    print("\n[1] mod_exp(3, 100, 1000) =", mod_exp(3, 100, 1000))

    key = AES.generate_key()
    aes = AES(key)
    message = b"Secure exam submission content."
    iv, ct = aes.encrypt_cbc(message)
    pt = aes.decrypt_cbc(ct, iv)
    print("\n[2] AES CBC Match:", message == pt)

    rsa = RSA.generate_keys(bits=1024)
    secret = b"AES-SESSION-KEY!"
    print("\n[3] RSA Match:", secret == rsa.decrypt(rsa.encrypt(secret)))

    exam = b"Hybrid encryption test."
    pkg = HybridCryptosystem.encrypt_submission(exam, "STU-1", "exam.txt", rsa)
    recovered = HybridCryptosystem.decrypt_submission(pkg, rsa)
    print("\n[4] Hybrid Match:", exam == recovered)


def main() -> None:
    parser = argparse.ArgumentParser(description="SecureExamSystem")
    parser.add_argument("--mode", choices=["ui", "demo"], default="ui")
    args = parser.parse_args()

    if args.mode == "demo":
        demo_console()
    else:
        run_ui()


if __name__ == "__main__":
    main()
