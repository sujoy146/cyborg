# ═══════════════════════════════════════════════════════════════
#  pipeline_sender.py — Full sender-side demo
#
#  Demonstrates the complete flow:
#    message → lookup table → ref_number → encrypt → 60 bits
#    → StegoGAN G → stego image → save
#
#  Usage:
#    python pipeline_sender.py
# ═══════════════════════════════════════════════════════════════

from lookup_table import add_message
from encryption import encrypt


def sender_pipeline(message: str, pin: str, salt: str) -> dict:
    """
    Full sender pipeline (minus StegoGAN G, which needs the model).

    Args:
        message: Arbitrary-length text to encode
        pin:     Pre-shared PIN
        salt:    Pre-shared salt

    Returns:
        dict with ref_number and the 60-bit array
    """
    # Step 1: Store message, get reference number
    ref_number = add_message(message)
    print(f"  [1] Message stored -> ref_number = {ref_number}")

    # Step 2: Encrypt ref_number → 60 bits
    bits_60 = encrypt(int(ref_number), pin, salt)
    print(f"  [2] Encrypted -> {len(bits_60)} wire bits")
    print(f"      First 20 bits (encrypted data): {bits_60[::3]}")

    return {
        "ref_number": ref_number,
        "bits_60": bits_60,
    }


# ── Demo ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  CYBORG - Sender Pipeline Demo")
    print("=" * 60)

    # Pre-shared secrets (both parties must know these)
    PIN  = "1234"
    SALT = "cyborg_demo"

    messages = [
        "send money to sujoy",
        "account number 9876543210",
        "hello sujoy how are you",
        "send money to sujoy",  # duplicate — should return same ref
    ]

    for msg in messages:
        print(f"\n-> Message: \"{msg}\"")
        result = sender_pipeline(msg, PIN, SALT)
        print(f"  [OK] Ready to feed {len(result['bits_60'])} bits into StegoGAN G")

    print("\n" + "=" * 60)
    print("  Done. In production, bits_60 -> StegoGAN G(image, bits) -> stego.png")
    print("=" * 60)
