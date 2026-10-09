"""Definition of the 8 ORM duel questions.

Each question has:
- ``n``: number (1-8)
- ``text``: what is being asked (English, matching the lab)
- ``reference``: a trusted ORM QuerySet that yields the canonical answer
- ``serialize``: turns a QuerySet into a comparable list of primitives

The duel compares ``team`` and ``ai`` answers against ``reference`` using
``serialize``. ``reference`` is written independently and simply so it acts
as ground truth for the seed data created by ``seed_blog``.
"""
from __future__ import annotations

from django.db.models import Count, Q

from blog.models import Author, Category, Post

PUBLISHED = Q(posts__is_published=True)


# --- Serializers ------------------------------------------------------------

def _post_slugs(qs):
    return list(qs.values_list("slug", flat=True))


def _author_counts(qs):
    return [(name, n) for name, n in qs.values_list("name", "n_posts")]


def _category_counts(qs):
    return [(slug, n) for slug, n in qs.values_list("slug", "n_posts")]


def _post_comment_tag_counts(qs):
    return [
        (slug, nc, nt)
        for slug, nc, nt in qs.values_list("slug", "n_comments", "n_tags")
    ]


# --- Reference (ground-truth) implementations -------------------------------

def _ref_q1():
    """All published posts, newest first."""
    return Post.objects.filter(is_published=True).order_by("-published_at")


def _ref_q2():
    """Published posts that have a category, ordered by title."""
    return (
        Post.objects.filter(is_published=True, category__isnull=False)
        .order_by("title")
    )


def _ref_q3():
    """Published posts by ana@blog.test, newest first."""
    return (
        Post.objects.filter(is_published=True, author__email="ana@blog.test")
        .order_by("-published_at")
    )


def _ref_q4():
    """Distinct published posts tagged 'python', newest first."""
    return (
        Post.objects.filter(is_published=True, tags__slug="python")
        .distinct()
        .order_by("-published_at")
    )


def _ref_q5():
    """Published posts annotated with n_comments and n_tags."""
    return (
        Post.objects.filter(is_published=True)
        .annotate(
            n_comments=Count("comments", distinct=True),
            n_tags=Count("tags", distinct=True),
        )
        .order_by("-n_comments", "title")
    )


def _ref_q6():
    """Authors with >=1 published post, annotated with n_posts."""
    return (
        Author.objects.annotate(
            n_posts=Count("posts", filter=PUBLISHED, distinct=True)
        )
        .filter(n_posts__gte=1)
        .order_by("-n_posts", "name")
    )


def _ref_q7():
    """Categories annotated with the number of published posts."""
    return (
        Category.objects.annotate(
            n_posts=Count("posts", filter=PUBLISHED, distinct=True)
        )
        .order_by("-n_posts", "name")
    )


def _ref_q8():
    """Published posts with at least 3 comments, most commented first."""
    return (
        Post.objects.filter(is_published=True)
        .annotate(n_comments=Count("comments", distinct=True))
        .filter(n_comments__gte=3)
        .order_by("-n_comments", "title")
    )


QUESTIONS = [
    {
        "n": 1,
        "text": "All published posts, newest first (return a Post QuerySet).",
        "reference": _ref_q1,
        "serialize": _post_slugs,
    },
    {
        "n": 2,
        "text": "Published posts that have a category, ordered by title.",
        "reference": _ref_q2,
        "serialize": _post_slugs,
    },
    {
        "n": 3,
        "text": "Published posts by the author ana@blog.test, newest first.",
        "reference": _ref_q3,
        "serialize": _post_slugs,
    },
    {
        "n": 4,
        "text": "Distinct published posts tagged 'python', newest first.",
        "reference": _ref_q4,
        "serialize": _post_slugs,
    },
    {
        "n": 5,
        "text": "Published posts annotated with n_comments and n_tags, "
                "ordered by comments desc then title.",
        "reference": _ref_q5,
        "serialize": _post_comment_tag_counts,
    },
    {
        "n": 6,
        "text": "Authors with >=1 published post, annotated with n_posts, "
                "ordered by count desc then name.",
        "reference": _ref_q6,
        "serialize": _author_counts,
    },
    {
        "n": 7,
        "text": "Categories annotated with the number of published posts, "
                "ordered by count desc then name.",
        "reference": _ref_q7,
        "serialize": _category_counts,
    },
    {
        "n": 8,
        "text": "Published posts with at least 3 comments, "
                "most commented first.",
        "reference": _ref_q8,
        "serialize": _post_slugs,
    },
]
