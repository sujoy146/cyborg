# ═══════════════════════════════════════════════════════════════
#  pipeline_receiver.py — Full receiver-side demo
#
#  Demonstrates the complete flow:
#    stego image → StegoGAN R → 60 bits → decrypt → ref_number
#    → lookup table → original message
#
#  Usage:
#    python pipeline_receiver.py
# ═══════════════════════════════════════════════════════════════

from decryption import decrypt
from lookup_table import get_message


def receiver_pipeline(bits_60: list[int], pin: str, salt: str) -> dict:
    """
    Full receiver pipeline (minus StegoGAN R, which needs the model).

    Args:
        bits_60: 60-bit list extracted by StegoGAN R
        pin:     Pre-shared PIN
        salt:    Pre-shared salt

    Returns:
        dict with ref_number and the original message
    """
    # Step 1: Decrypt 60 bits → ref_number
    ref_number = decrypt(bits_60, pin, salt)
    print(f"  [1] Decrypted -> ref_number = {ref_number}")

    # Step 2: Look up original message
    message = get_message(ref_number)
    if message:
        print(f"  [2] Lookup -> \"{message}\"")
    else:
        print(f"  [2] Lookup -> NOT FOUND (token {ref_number} not in table)")

    return {
        "ref_number": ref_number,
        "message": message,
    }


# ── Demo ──────────────────────────────────────────────────────

if __name__ == "__main__":
    # This demo requires pipeline_sender.py to have been run first
    # (so that table.json has entries)
    from encryption import encrypt
    from lookup_table import add_message

    print("=" * 60)
    print("  CYBORG - Receiver Pipeline Demo")
    print("=" * 60)

    PIN  = "1234"
    SALT = "cyborg_demo"

    # Simulate: sender encodes a message
    test_message = "send money to sujoy"
    print(f"\n[Sender] Encoding: \"{test_message}\"")
    ref = add_message(test_message)
    bits_60 = encrypt(int(ref), PIN, SALT)
    print(f"[Sender] ref={ref}, bits sent to StegoGAN G")

    # Simulate: receiver gets the same bits from StegoGAN R
    # (In reality, StegoGAN R extracts these from the stego image)
    print(f"\n[Receiver] Got 60 bits from StegoGAN R:")
    result = receiver_pipeline(bits_60, PIN, SALT)

    # Verify round-trip
    print(f"\n{'=' * 60}")
    if result["message"] == test_message:
        print(f"  [OK] ROUND-TRIP SUCCESS")
        print(f"     Sent:     \"{test_message}\"")
        print(f"     Received: \"{result['message']}\"")
        print(f"     Token:    {result['ref_number']}")
    else:
        print(f"  [FAIL] ROUND-TRIP FAILED")
        print(f"     Sent:     \"{test_message}\"")
        print(f"     Received: \"{result['message']}\"")
    print("=" * 60)

    # Test with wrong PIN (should fail)
    print(f"\n[Attack] Trying wrong PIN...")
    wrong_result = receiver_pipeline(bits_60, "9999", SALT)
    print(f"  -> Got token {wrong_result['ref_number']} -> message: {wrong_result['message']}")
    print(f"  -> {'[FAIL] Decryption produced garbage (expected)' if wrong_result['message'] != test_message else '[WARN] Unexpectedly matched!'}")
