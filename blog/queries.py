"""Query helpers for the blog front page.

Lab 07 optimization
-------------------
The front page shows each published post with its author, its category and
its comments. The naive version triggered N+1: 1 query for the posts, then
one query per post for the author, one for the category and one for the
comments (1 + 3N).

Optimization strategy:
- ``select_related('author', 'category')`` follows the ForeignKeys with a SQL
  JOIN, fetching posts + author + category in a single query.
- ``prefetch_related('comments')`` fetches all comments of all shown posts in
  one extra query and stitches them in Python (correct for reverse FK).

Result: 2 queries total, regardless of the number of posts.
"""
from __future__ import annotations

from .models import Post


def get_front_page_posts():
    """Return published posts, newest first (optimized, 2 queries)."""
    return (
        Post.objects.filter(is_published=True)
        .select_related("author", "category")
        .prefetch_related("comments")
        .order_by("-published_at")
    )
