# ═══════════════════════════════════════════════════════════════
#  crypto.py — AES-256-GCM authenticated encryption
#
#  Layer 1 of the 5-layer security pipeline.
#  Encrypts the user's message BEFORE it enters the lookup table,
#  so table.json only ever stores ciphertext — never plaintext.
#
#  Key derivation: PBKDF2-HMAC-SHA256 (100,000 iterations)
#  Cipher: AES-256-GCM (authenticated encryption with 96-bit nonce)
#  Output: base64(nonce + ciphertext + tag)
# ═══════════════════════════════════════════════════════════════

import hashlib
import os
import base64

# Use PyCryptodome for AES-GCM
from Crypto.Cipher import AES


def _derive_aes_key(pin: str, salt: str) -> bytes:
    """
    Derive a 256-bit AES key from PIN + salt using PBKDF2.

    Uses domain-separated salt ('cyborg-aes:' prefix) so the AES key
    is cryptographically independent from the XOR key, even though
    the user enters the same PIN+salt once.

    100,000 iterations (OWASP recommendation), SHA-256.
    """
    return hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode('utf-8'),
        ('cyborg-aes:' + salt).encode('utf-8'),
        iterations=100_000,
        dklen=32,  # 256 bits
    )


def aes_encrypt(plaintext: str, pin: str, salt: str) -> str:
    """
    Encrypt a plaintext message using AES-256-GCM.

    Args:
        plaintext: The message to encrypt
        pin:  Pre-shared PIN string
        salt: Pre-shared salt string

    Returns:
        Base64-encoded string containing: nonce (12B) + ciphertext + tag (16B)
        This is what gets stored in the lookup table.
    """
    key = _derive_aes_key(pin, salt)
    nonce = os.urandom(12)  # 96-bit random nonce (GCM standard)

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))

    # Pack: nonce + ciphertext + tag → base64
    packed = nonce + ciphertext + tag
    return base64.b64encode(packed).decode('ascii')


def aes_decrypt(encoded: str, pin: str, salt: str) -> str | None:
    """
    Decrypt an AES-256-GCM encrypted message.

    Args:
        encoded: Base64 string from aes_encrypt()
        pin:  Pre-shared PIN string
        salt: Pre-shared salt string

    Returns:
        Original plaintext string, or None if decryption fails
        (wrong PIN/salt or tampered data)
    """
    try:
        key = _derive_aes_key(pin, salt)
        packed = base64.b64decode(encoded)

        # Unpack: nonce (12B) + ciphertext (variable) + tag (16B)
        nonce = packed[:12]
        tag = packed[-16:]
        ciphertext = packed[12:-16]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')
    except (ValueError, KeyError):
        # Authentication failed — wrong PIN/salt or tampered data
        return None
