"""Team answers to the 8 ORM duel questions.

Every function returns a Django QuerySet (lazy). The functions are written
to be efficient: aggregations use ``Count(..., distinct=True)`` so joins do
not multiply rows, and M2M/reverse relations that are only filtered use
``distinct()`` where needed.

Naming: ``answer_q1`` .. ``answer_q8``.
"""
from __future__ import annotations

from django.db.models import Count, Q

from blog.models import Author, Category, Post

_PUBLISHED = Q(posts__is_published=True)


def answer_q1():
    """All published posts, newest first."""
    return Post.objects.filter(is_published=True).order_by("-published_at")


def answer_q2():
    """Published posts that have a category, ordered by title."""
    return (
        Post.objects.filter(is_published=True, category__isnull=False)
        .order_by("title")
    )


def answer_q3():
    """Published posts by ana@blog.test, newest first."""
    return (
        Post.objects.filter(is_published=True, author__email="ana@blog.test")
        .order_by("-published_at")
    )


def answer_q4():
    """Distinct published posts tagged 'python', newest first."""
    return (
        Post.objects.filter(is_published=True, tags__slug="python")
        .distinct()
        .order_by("-published_at")
    )


def answer_q5():
    """Published posts annotated with n_comments and n_tags."""
    return (
        Post.objects.filter(is_published=True)
        .annotate(
            n_comments=Count("comments", distinct=True),
            n_tags=Count("tags", distinct=True),
        )
        .order_by("-n_comments", "title")
    )


def answer_q6():
    """Authors with >=1 published post, annotated with n_posts."""
    return (
        Author.objects.annotate(
            n_posts=Count("posts", filter=_PUBLISHED, distinct=True)
        )
        .filter(n_posts__gte=1)
        .order_by("-n_posts", "name")
    )


def answer_q7():
    """Categories annotated with the number of published posts."""
    return (
        Category.objects.annotate(
            n_posts=Count("posts", filter=_PUBLISHED, distinct=True)
        )
        .order_by("-n_posts", "name")
    )


def answer_q8():
    """Published posts with at least 3 comments, most commented first."""
    return (
        Post.objects.filter(is_published=True)
        .annotate(n_comments=Count("comments", distinct=True))
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
