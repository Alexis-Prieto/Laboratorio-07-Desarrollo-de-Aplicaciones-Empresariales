"""Management command wrapping the controlled agent executor.

Examples:
    python manage.py agent --intent list_posts
    python manage.py agent --intent comments_of_post --post-id 1
    python manage.py agent --intent delete_comments_of_post --post-id 5
    python manage.py agent --intent delete_comments_of_post --post-id 5 \
        --approve <HASH>
    python manage.py agent --intent drop_table
    python manage.py agent --intent raw_sql
"""
from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from blog.agent import executor


class Command(BaseCommand):
    help = "Run a single agent intent under the safety model."

    def add_arguments(self, parser):
        parser.add_argument("--intent", required=True)
        parser.add_argument("--post-id", dest="post_id", default=None)
        parser.add_argument("--approve", dest="approve", default=None)

    def handle(self, *args, **options):
        intent = options["intent"]
        params = {}
        if options["post_id"] is not None:
            params["post_id"] = options["post_id"]

        result = executor.run(intent, params, approve_hash=options["approve"])

        status = result["status"]
        style = {
            executor.STATUS_OK: self.style.SUCCESS,
            executor.STATUS_APPROVAL_REQUIRED: self.style.WARNING,
            executor.STATUS_DENIED: self.style.ERROR,
        }.get(status, self.style.WARNING)

        self.stdout.write(style(f"[{status}] intent={intent}"))
        if "reason" in result:
            self.stdout.write(f"  reason: {result['reason']}")
        if "hash" in result:
            self.stdout.write(f"  plan hash: {result['hash']}")
        # Full machine-readable result for scripting/inspection.
        self.stdout.write("--- result json ---")
        self.stdout.write(json.dumps(result, indent=2, default=str))
