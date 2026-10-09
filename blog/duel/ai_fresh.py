"""Fresh-from-scratch AI answers (Lab Paso 8).

These simulate asking an assistant to write the 8 queries given ONLY the
model descriptions, without seeing the repo. They are compared against the
same reference used by the main duel. The intent is to observe whether the
failure modes differ from the guided run (Paso 6/7).

Failure modes here (different from ai.py):
- Q1: forgot the published filter (boundary/misread).
- Q2: ordered but returned ALL posts (misread "that have a category").
- Q3: filtered by author NAME with wrong case/space (invented lookup value).
- Q4: forgot distinct() -> duplicate rows for multi... (counts multiplied).
- Q5: correct.
- Q6: counted all posts instead of published only (misread).
- Q7: correct.
- Q8: used >= 3 but forgot the published filter (boundary).
"""
from __future__ import annotations

from django.db.models import Count

from blog.models import Author, Category, Post


def answer_q1():
    """Fresh Q1: forgot is_published filter."""
    return Post.objects.order_by("-published_at")


def answer_q2():
    """Fresh Q2: returned all posts (ignored 'that have a category')."""
    return Post.objects.filter(is_published=True).order_by("title")


def answer_q3():
    """Fresh Q3: filtered by author name with a wrong value."""
    return (
        Post.objects.filter(author__name="ana torres")
        .order_by("-published_at")
    )


def answer_q4():
    """Fresh Q4: forgot distinct() -> duplicate posts per matching tag row."""
    return (
        Post.objects.filter(is_published=True, tags__slug="python")
        .order_by("-published_at")
    )


def answer_q5():
    """Fresh Q5: correct annotation."""
    return (
        Post.objects.filter(is_published=True)
        .annotate(
            n_comments=Count("comments", distinct=True),
            n_tags=Count("tags", distinct=True),
        )
        .order_by("-n_comments", "title")
    )


def answer_q6():
    """Fresh Q6: counted all posts (not only published)."""
    return (
        Author.objects.annotate(n_posts=Count("posts"))
        .filter(n_posts__gte=1)
        .order_by("-n_posts", "name")
    )


def answer_q7():
    """Fresh Q7: correct."""
    from django.db.models import Q

    return (
        Category.objects.annotate(
            n_posts=Count("posts", filter=Q(posts__is_published=True), distinct=True)
        )
        .order_by("-n_posts", "name")
    )


def answer_q8():
    """Fresh Q8: forgot the published filter (includes drafts)."""
    return (
        Post.objects.annotate(n_comments=Count("comments", distinct=True))
        .filter(n_comments__gte=3)
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
