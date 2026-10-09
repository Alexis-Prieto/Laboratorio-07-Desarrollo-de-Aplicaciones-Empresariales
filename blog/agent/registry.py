"""Registry of allowed agent intents and their safety rules.

This is the security core of the controlled agent. An intent is only executed
if it appears in ``INTENTS``. Each entry declares:

- ``destructive``: whether it mutates/deletes data. Destructive intents
  REQUIRE human approval (a valid plan hash) before running.
- ``params``: the accepted parameters with a validator callable. Unknown
  parameters are rejected, which blocks prompt-injection payloads that try to
  smuggle extra arguments.

Anything not listed here (``drop_table``, ``raw_sql``, arbitrary keywords) is
DENIED. There is no code path that executes raw SQL or schema changes.
"""
from __future__ import annotations

# Allowed values are intentionally tiny whitelists.
ALLOWED_INTENTS = ("list_posts", "comments_of_post", "delete_comments_of_post")
DENIED_INTENTS = ("drop_table", "raw_sql")


def _validate_post_id(value):
    """Validate that a post id is a positive integer."""
    try:
        post_id = int(value)
    except (TypeError, ValueError):
        raise ValueError("post-id must be an integer")
    if post_id <= 0:
        raise ValueError("post-id must be a positive integer")
    return post_id


def _no_params(_value=None):
    return True


INTENTS = {
    "list_posts": {
        "destructive": False,
        "params": {},  # no parameters accepted
        "description": "List published posts (read-only).",
    },
    "comments_of_post": {
        "destructive": False,
        "params": {"post_id": _validate_post_id},
        "description": "List comments of a given post (read-only).",
    },
    "delete_comments_of_post": {
        "destructive": True,  # requires approval
        "params": {"post_id": _validate_post_id},
        "description": "Delete all comments of a given post (destructive).",
    },
}


def is_known_intent(intent):
    return intent in INTENTS


def is_denied_intent(intent):
    return intent in DENIED_INTENTS


def requires_approval(intent):
    entry = INTENTS.get(intent)
    return bool(entry and entry["destructive"])


def validate_params(intent, params):
    """Validate and normalize the parameters for an intent.

    Raises ValueError on unknown parameters or invalid values. This is what
    stops an injected instruction from adding parameters such as
    ``--force`` or ``--all-users``.
    """
    if intent not in INTENTS:
        raise ValueError(f"unknown intent: {intent}")
    allowed = INTENTS[intent]["params"]
    unknown = set(params) - set(allowed)
    if unknown:
        raise ValueError(
            f"unexpected parameter(s) for '{intent}': {sorted(unknown)}"
        )
    normalized = {}
    for key, validator in allowed.items():
        if key in params:
            normalized[key] = validator(params[key])
    return normalized
