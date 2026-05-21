export function validateMessage(msg) {
  const errors = [];
  const warnings = [];

  if (!msg || msg.trim().length === 0) {
    errors.push("Message is required");
    return { valid: false, errors, warnings };
  }

  // No charset or length restriction — the backend maps any message
  // to a 6-digit reference number via the lookup table.

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

export function validatePin(pin) {
  if (!pin || pin.trim().length === 0) {
    return { valid: false, errors: ["PIN is required"], warnings: [] };
  }
  return { valid: true, errors: [], warnings: [] };
}

export function validateSalt(salt) {
  if (!salt || salt.trim().length === 0) {
    return { valid: false, errors: ["Salt is required"], warnings: [] };
  }
  return { valid: true, errors: [], warnings: [] };
}

export function validateAllEncode(message, pin, salt) {
  const m = validateMessage(message);
  const p = validatePin(pin);
  const s = validateSalt(salt);

  return {
    valid: m.valid && p.valid && s.valid,
    message: m,
    pin: p,
    salt: s,
  };
}

export function validateAllDecode(pin, salt) {
  const p = validatePin(pin);
  const s = validateSalt(salt);

  return {
    valid: p.valid && s.valid,
    pin: p,
    salt: s,
  };
}
