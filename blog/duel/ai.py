"""Simulated AI answers to the 8 ORM duel questions.

These mimic what a generic assistant might produce. Some are correct, others
contain representative defects so the lab can classify AI failures:

- Q2: misread the question (returns posts WITHOUT a category).
- Q3: invented field ``author__nickname`` (raises FieldError).
- Q5: counts multiplied (Count without distinct over comments AND tags).
- Q7: correct result but expensive (N+1 loop before returning).
- Q8: off-by-one boundary (uses ``> 3`` instead of ``>= 3``).
- Q1, Q4, Q6: correct.

Each function returns a QuerySet, matching the team contract.
"""
from __future__ import annotations

from django.db.models import Count, Q

from blog.models import Author, Category, Post

_PUBLISHED = Q(posts__is_published=True)


def answer_q1():
    """All published posts, newest first. (Correct.)"""
    return Post.objects.filter(is_published=True).order_by("-published_at")


def answer_q2():
    """Misread: returns published posts WITHOUT a category (isnull=True)."""
    return (
        Post.objects.filter(category__isnull=True)
        .order_by("title")
    )


def answer_q3():
    """Invented field: Author has no 'nickname' field."""
    return (
        Post.objects.filter(author__nickname="ana@blog.test")
        .order_by("-published_at")
    )


def answer_q4():
    """Distinct published posts tagged 'python', newest first. (Correct.)"""
    return (
        Post.objects.filter(is_published=True, tags__slug="python")
        .distinct()
        .order_by("-published_at")
    )


def answer_q5():
    """Counts multiplied: no distinct -> cartesian product comments x tags."""
    return (
        Post.objects.filter(is_published=True)
        .annotate(
            n_comments=Count("comments"),
            n_tags=Count("tags"),
        )
        .order_by("-n_comments", "title")
    )


def answer_q6():
    """Authors with >=1 published post, annotated with n_posts. (Correct.)"""
    return (
        Author.objects.annotate(
            n_posts=Count("posts", filter=_PUBLISHED, distinct=True)
        )
        .filter(n_posts__gte=1)
        .order_by("-n_posts", "name")
    )


def answer_q7():
    """Correct result but expensive: warms an N+1 loop before returning."""
    warming = list(
        Category.objects.annotate(
            n_posts=Count("posts", filter=_PUBLISHED, distinct=True)
        )
    )
    for category in warming:
        list(category.posts.all())  # one extra query per category (N+1)
    return (
        Category.objects.annotate(
            n_posts=Count("posts", filter=_PUBLISHED, distinct=True)
        )
        .order_by("-n_posts", "name")
    )


def answer_q8():
    """Boundary bug: uses > 3 instead of >= 3 (drops posts with exactly 3)."""
    return (
        Post.objects.filter(is_published=True)
        .annotate(n_comments=Count("comments", distinct=True))
        .filter(n_comments__gt=3)
        .order_by("-n_comments", "title")
    )


ANSWERS = {
    1: answer_q1,
    2: answer_q2,
    3: answer_q3,
    4: answer_q4,
    5: answer_q5,
    6: answer_q6,
    7: answer_q7,
    8: answer_q8,
}
