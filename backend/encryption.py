# ═══════════════════════════════════════════════════════════════
#  encryption.py — Token → 6-bit XOR+PBKDF2 → 60-bit ECC
#
#  6 data bits × 10× repetition = 60 wire bits
#  Max ref numbers : 63  (2^6 - 1, starting from 000001)
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


def _int_to_bits(value: int, num_bits: int = 6) -> list[int]:
    """Convert integer to big-endian bit list."""
    if value < 0 or value > (2 ** num_bits - 1):
        raise ValueError(f"Value {value} out of range for {num_bits} bits (max {2**num_bits - 1})")
    return [int(b) for b in format(value, f'0{num_bits}b')]


def encrypt(ref_number: int, pin: str, salt: str) -> list[int]:
    """
    Encrypt a reference number into a 60-bit array for StegoGAN G.

    Pipeline:
        1. ref_number (int 1–63) → 6 binary bits
        2. XOR with PBKDF2-derived 6 key bits
        3. 10× repetition ECC → 60 wire bits

    Args:
        ref_number : Integer 1–63
        pin        : Pre-shared PIN string
        salt       : Pre-shared salt string

    Returns: list of 60 ints (0/1), ready for StegoGAN G
    """
    if ref_number < 1 or ref_number > 63:
        raise ValueError(f"ref_number must be 1–63, got {ref_number}")

    # Step 1: Integer → 6 bits
    data_bits = _int_to_bits(ref_number, 6)

    # Step 2: XOR with PBKDF2 key bits
    key_bits = _derive_key_bits(pin, salt, 6)
    encrypted_bits = [d ^ k for d, k in zip(data_bits, key_bits)]

    # Step 3: 10× repetition ECC → 60 wire bits
    ecc_bits = []
    for b in encrypted_bits:
        ecc_bits.extend([b] * 10)

    return ecc_bits   # 6 × 10 = 60 bits → StegoGAN G
