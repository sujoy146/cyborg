# ═══════════════════════════════════════════════════════════════
#  lookup_table.py — Persistent JSON-backed lookup table
#
#  Maps 6-digit reference numbers to arbitrary messages.
#  Max entries : 63  (matches 6-bit ECC payload capacity)
#  Active cap  : 55  (circular eviction keeps oldest 8 expired)
#  Auto-assigns sequential tokens. Survives restarts.
# ═══════════════════════════════════════════════════════════════

import json
import os

# Use /data on HF Spaces (writable persistent dir), fallback to local for dev
_DATA_DIR = "/data" if os.path.isdir("/data") else os.path.dirname(os.path.abspath(__file__))
TABLE_FILE = os.path.join(_DATA_DIR, "table.json")

_SCHEMA_VERSION = 2
_MAX_POSITION   = 63          # 2^6 - 1  (ref numbers 000001 → 000063)
_ACTIVE_CAP     = 55          # max active entries before eviction kicks in


def _empty_table():
    return {
        "version": _SCHEMA_VERSION,
        "next_id": 1,             # next ref number to assign (1–63, wraps)
        "entries": {},            # { "000001": "ciphertext...", ... }
    }


def _load():
    if not os.path.exists(TABLE_FILE):
        return _empty_table()
    try:
        with open(TABLE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "entries" not in data:
            return _empty_table()
        # Migrate from v1 (no next_id) → v2
        if "next_id" not in data:
            entries = data.get("entries", {})
            if entries:
                max_num = max(int(k) for k in entries.keys())
                data["next_id"] = (max_num % _MAX_POSITION) + 1
            else:
                data["next_id"] = 1
            data["version"] = _SCHEMA_VERSION
        return data
    except (json.JSONDecodeError, IOError):
        return _empty_table()


def _save(table):
    """Atomic write — prevents corruption on crash mid-write."""
    tmp = TABLE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2, ensure_ascii=False)
    if os.path.exists(TABLE_FILE):
        os.replace(tmp, TABLE_FILE)
    else:
        os.rename(tmp, TABLE_FILE)


def _oldest_ref(entries: dict) -> str | None:
    """Return the ref number with the lowest integer value (oldest sequential)."""
    if not entries:
        return None
    return min(entries.keys(), key=lambda k: int(k))


# ── Public API ────────────────────────────────────────────────


def add_message(text: str) -> str:
    """
    Add a message to the lookup table.

    Returns existing ref number if message already exists.
    Otherwise assigns the next sequential number (000001–000063).
    When the table reaches 55 active entries, the oldest entry
    is evicted (FIFO) before the new one is inserted.

    Returns: 6-digit zero-padded reference number string (e.g. "000001")
    """
    table   = _load()
    entries = table["entries"]

    # Return existing ref if duplicate
    for ref, existing in entries.items():
        if existing == text:
            return ref

    # Evict oldest if at capacity (55 active entries)
    while len(entries) >= _ACTIVE_CAP:
        oldest = _oldest_ref(entries)
        if oldest:
            del entries[oldest]

    # Assign at next_id position
    ref = f"{table['next_id']:06d}"

    # If this slot somehow still has data (after wrap), evict it
    if ref in entries:
        del entries[ref]

    entries[ref] = text

    # Advance next_id: 1 → 2 → ... → 63 → 1 → 2 → ...
    table["next_id"] = (table["next_id"] % _MAX_POSITION) + 1

    _save(table)
    return ref


def get_message(ref_number: str) -> str | None:
    """Return message for ref_number, or None if not found."""
    return _load()["entries"].get(ref_number)


def list_entries() -> dict:
    """Return all entries as {ref_number: message}."""
    return _load()["entries"]


def remove_entry(ref_number: str) -> bool:
    """Remove entry by ref number. Returns True if removed, False if not found."""
    table = _load()
    if ref_number in table["entries"]:
        del table["entries"][ref_number]
        _save(table)
        return True
    return False


def capacity() -> dict:
    """Return current usage vs max capacity."""
    entries = _load()["entries"]
    return {
        "used"     : len(entries),
        "max"      : _ACTIVE_CAP,
        "remaining": _ACTIVE_CAP - len(entries),
    }
