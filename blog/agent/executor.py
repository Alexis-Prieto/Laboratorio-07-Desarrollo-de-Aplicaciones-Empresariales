"""Controlled executor for the blog agent.

Safety model
------------
1. Whitelist: only intents in ``registry.INTENTS`` may run.
2. Denylist: ``drop_table`` / ``raw_sql`` are always denied (no code path
   exists to run raw SQL or schema changes).
3. Parameter validation: unknown or invalid parameters are rejected, which
   neutralizes prompt-injection payloads that try to smuggle extra args.
4. Human approval for destructive intents: a destructive action first returns
   a PLAN with a hash. The action only runs when ``--approve <hash>`` matches
   the CURRENT plan. The hash covers the affected rows, so if the data changes
   between planning and approval, the hash no longer matches and the action is
   rejected.
"""
from __future__ import annotations

import hashlib
import json

from django.db import transaction

from blog.models import Comment, Post
from blog.agent import registry

STATUS_OK = "ok"
STATUS_APPROVAL_REQUIRED = "approval_required"
STATUS_DENIED = "denied"


def _canonical(obj):
    """Return a canonical JSON string for hashing (stable key order)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _plan_hash(plan):
    """Hash a plan dict deterministically."""
    payload = _canonical(plan).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _affected_comment_ids(post_id):
    """Snapshot of the rows a destructive action would touch."""
    return sorted(
        Comment.objects.filter(post_id=post_id).values_list("id", flat=True)
    )


def build_plan(intent, params):
    """Build a plan for an intent. Returns a dict with a hash.

    The plan includes a snapshot of affected rows so the hash is bound to the
    current database state.
    """
    plan = {
        "intent": intent,
        "params": params,
    }
    if intent == "delete_comments_of_post":
        post_id = params["post_id"]
        plan["affected_comment_ids"] = _affected_comment_ids(post_id)
    return plan


def run(intent, params=None, approve_hash=None):
    """Execute an intent under the safety model.

    Returns a result dict: {"status": ..., ...}.
    """
    params = params or {}

    # 1) Explicit denylist first (never any code path for these).
    if registry.is_denied_intent(intent):
        return {
            "status": STATUS_DENIED,
            "intent": intent,
            "reason": "intent is explicitly denied (no raw SQL / DDL allowed)",
        }

    # 2) Whitelist check.
    if not registry.is_known_intent(intent):
        return {
            "status": STATUS_DENIED,
            "intent": intent,
            "reason": "intent is not in the whitelist",
        }

    # 3) Parameter validation (blocks injected extra parameters).
    try:
        clean_params = registry.validate_params(intent, params)
    except ValueError as exc:
        return {
            "status": STATUS_DENIED,
            "intent": intent,
            "reason": f"invalid parameters: {exc}",
        }

    # 4) Destructive intents require a matching approval hash.
    if registry.requires_approval(intent):
        plan = build_plan(intent, clean_params)
        current_hash = _plan_hash(plan)
        if approve_hash is None:
            return {
                "status": STATUS_APPROVAL_REQUIRED,
                "intent": intent,
                "params": clean_params,
                "plan": plan,
                "hash": current_hash,
                "reason": "destructive action requires human approval",
            }
        if approve_hash != current_hash:
            return {
                "status": STATUS_DENIED,
                "intent": intent,
                "reason": "approval hash does not match the current plan "
                          "(the data changed after planning)",
                "expected_hash": current_hash,
            }
        # Approved and still valid -> execute inside a transaction.
        with transaction.atomic():
            deleted, _ = Comment.objects.filter(
                post_id=clean_params["post_id"]
            ).delete()
        return {
            "status": STATUS_OK,
            "intent": intent,
            "params": clean_params,
            "deleted_comments": deleted,
        }

    # 5) Read-only intents.
    if intent == "list_posts":
        posts = Post.objects.filter(is_published=True).order_by("-published_at")
        return {
            "status": STATUS_OK,
            "intent": intent,
            "posts": [
                {"id": p.id, "title": p.title, "slug": p.slug} for p in posts
            ],
        }

    if intent == "comments_of_post":
        post_id = clean_params["post_id"]
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return {
                "status": STATUS_OK,
                "intent": intent,
                "params": clean_params,
                "post": None,
                "comments": [],
            }
        comments = post.comments.all().order_by("created_at")
        return {
            "status": STATUS_OK,
            "intent": intent,
            "params": clean_params,
            "post": {"id": post.id, "title": post.title},
            "comments": [
                {
                    "id": c.id,
                    "author_name": c.author_name,
                    "body": c.body,
                }
                for c in comments
            ],
        }

    # Should be unreachable given the whitelist.
    return {"status": STATUS_DENIED, "intent": intent, "reason": "unhandled"}
