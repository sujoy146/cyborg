# ═══════════════════════════════════════════════════════════════
#  decryption.py — 60-bit ECC → XOR+PBKDF2 → Token
#
#  10× majority vote ECC → 6 data bits → XOR → ref number
#  P(clean decode) : ~96% at 86% raw bit accuracy
# ═══════════════════════════════════════════════════════════════

import hashlib


def _derive_key_bits(pin: str, salt: str, num_bits: int = 6) -> list[int]:
    """
    Derive key bits from PIN + salt using PBKDF2.

    Uses domain-separated salt ('cyborg-xor:' prefix) so the XOR key
    is cryptographically independent from the AES key.

    Extracts bits from the first byte of the 32-byte PBKDF2 output,
    big-endian, and takes exactly `num_bits` bits (default 6).

    MUST be identical in encryption.py and decryption.py.
    """
    key_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode(),
        ('cyborg-xor:' + salt).encode(),
        100_000,
        dklen=32,
    )
    key_bits = []
    for byte in key_bytes[:1]:              # 1 byte = 8 bits, take first 6
        for i in range(7, -1, -1):
            key_bits.append((byte >> i) & 1)
    return key_bits[:num_bits]             # exactly 6 bits


def _bits_to_int(bits: list[int]) -> int:
    """Convert big-endian bit list to integer."""
    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def decrypt(bits_60: list[int], pin: str, salt: str) -> str:
    """
    Decrypt a 60-bit array back to a 6-digit reference number.

    Pipeline:
        1. 60 wire bits → 10× majority vote ECC → 6 encrypted bits
        2. XOR with PBKDF2-derived 6 key bits
        3. 6 bits → integer → 6-digit zero-padded string

    Args:
        bits_60 : list of 60 ints (0/1) from StegoGAN R
        pin     : Pre-shared PIN string
        salt    : Pre-shared salt string

    Returns: 6-digit zero-padded string (e.g. "000001")
    """
    if len(bits_60) != 60:
        raise ValueError(f"Expected 60 bits, got {len(bits_60)}")

    # Step 1: 10× majority vote ECC → 6 data bits
    # Each group of 10 bits votes: need > 5 (i.e. ≥ 6) for bit = 1
    data_bits = []
    for i in range(6):
        group = bits_60[i * 10 : i * 10 + 10]
        vote = 1 if sum(group) > 5 else 0
        data_bits.append(vote)

    # Step 2: XOR with PBKDF2 key bits
    key_bits = _derive_key_bits(pin, salt, 6)
    decrypted_bits = [d ^ k for d, k in zip(data_bits, key_bits)]

    # Step 3: Bits → integer → 6-digit string
    value = _bits_to_int(decrypted_bits)

    # Clamp to valid range (1–63) in case of residual bit errors
    if value < 1 or value > 63:
        value = max(1, value % 64)

    return f"{value:06d}"
