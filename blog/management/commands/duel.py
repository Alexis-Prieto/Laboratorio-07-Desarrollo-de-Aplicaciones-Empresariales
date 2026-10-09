"""Run the ORM duel: team vs reference, or ai vs reference.

Usage:
    python manage.py duel                 # compares team answers
    python manage.py duel --source ai      # compares AI answers

For each of the 8 questions the chosen source is executed, serialized and
compared against the trusted reference. Exceptions are captured and shown as
errors (e.g. an AI answer using a non-existent field).
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import connection

from blog.duel import ai as ai_module
from blog.duel import ai_fresh as ai_fresh_module
from blog.duel import questions
from blog.duel import team as team_module

SOURCES = {
    "team": team_module.ANSWERS,
    "ai": ai_module.ANSWERS,
    "ai_fresh": ai_fresh_module.ANSWERS,
}


class Command(BaseCommand):
    help = "Run the 8-question ORM duel against the reference answers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default="team",
            choices=sorted(SOURCES),
            help="Which answer set to evaluate (default: team).",
        )

    def _evaluate(self, fn, serialize):
        """Return (ok, value_or_error, n_queries)."""
        before = len(connection.queries)
        try:
            value = serialize(fn())
        except Exception as exc:  # noqa: BLE001 - we want to report any error
            return False, f"{type(exc).__name__}: {exc}", None
        after = len(connection.queries)
        return True, value, after - before

    def handle(self, *args, **options):
        source = options["source"]
        answers = SOURCES[source]
        passed = 0

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"=== ORM DUEL — source: {source} ==="
            )
        )

        for q in questions.QUESTIONS:
            n = q["n"]
            expected = q["serialize"](q["reference"]())

            ok, value, n_queries = self._evaluate(answers[n], q["serialize"])

            if ok and value == expected:
                passed += 1
                status = self.style.SUCCESS("PASS")
                self.stdout.write(f"Q{n}: {status}  ({n_queries} queries)")
            else:
                status = self.style.ERROR("FAIL")
                self.stdout.write(f"Q{n}: {status}")
                self.stdout.write(f"    question : {q['text']}")
                self.stdout.write(f"    expected : {expected}")
                self.stdout.write(f"    {source:>8} : {value}")

        total = len(questions.QUESTIONS)
        self.stdout.write("")
        self.stdout.write(f"Score: {passed}/{total} for source '{source}'")
        if passed == total:
            self.stdout.write(self.style.SUCCESS("All questions passed."))
        else:
            self.stdout.write(
                self.style.WARNING(f"{total - passed} question(s) failed.")
            )
