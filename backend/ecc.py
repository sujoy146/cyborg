# ═══════════════════════════════════════════════════════════════
#  ecc.py — 5-bit charset + ECC encode/decode (60-bit)
#
#  TODO: Paste your encode_message_ecc / decode_message_ecc
#        functions from Cell 9 of the 60-bit training notebook.
#
#  The constants below must match your training notebook exactly.
# ═══════════════════════════════════════════════════════════════

# 32 chars → 5 bits per char, index 0-31
CHAR_SET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ.!?#@"
BITS_PER_CHAR = 5
MSG_CHARS = 4          # max message length
DATA_BITS = MSG_CHARS * BITS_PER_CHAR  # 20
REP_FACTOR = 3         # 3× repetition ECC
TOTAL_BITS = DATA_BITS * REP_FACTOR    # 60


# ── Paste your ECC functions below this line ──
# def encode_message_ecc(message: str) -> list[int]: ...
# def decode_message_ecc(bits_60: list[int]) -> str: ...
