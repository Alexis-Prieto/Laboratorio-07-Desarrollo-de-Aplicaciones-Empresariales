"""Views for the blog app."""
from __future__ import annotations

from django.shortcuts import render

from .queries import get_front_page_posts


def front_page(request):
    """Render the list of published posts on the home page."""
    posts = get_front_page_posts()
    return render(request, "blog/front_page.html", {"posts": posts})
