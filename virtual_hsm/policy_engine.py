"""
Virtual HSM — Policy Engine
Controls which cryptographic operations are permitted.
"""

# Default policy — all standard operations allowed
_ALLOWED_OPERATIONS = {
    "generate_key":  True,
    "encrypt":       True,
    "decrypt":       True,
    "sign":          True,
    "verify":        True,
    "list_keys":     True,
    "rotate_password": True,
}


def check_policy(operation: str) -> bool:
    """
    Check whether a given operation is allowed by the HSM policy.
    Returns True if allowed, raises PermissionError if denied.
    """
    if operation not in _ALLOWED_OPERATIONS:
        raise PermissionError(f"Unknown operation: '{operation}'")
    
    if not _ALLOWED_OPERATIONS[operation]:
        raise PermissionError(
            f"Policy violation: operation '{operation}' is currently disabled."
        )
    return True


def set_policy(operation: str, allowed: bool):
    """Enable or disable a specific operation."""
    if operation not in _ALLOWED_OPERATIONS:
        raise ValueError(f"Unknown operation: '{operation}'")
    _ALLOWED_OPERATIONS[operation] = allowed


def get_policies() -> dict:
    """Return a copy of the current policy table."""
    return dict(_ALLOWED_OPERATIONS)
