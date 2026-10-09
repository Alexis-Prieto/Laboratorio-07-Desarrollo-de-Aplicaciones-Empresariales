"""Test that the front page does not suffer from the N+1 problem.

This test MUST pass from red (23 queries) to green (2 queries) by fixing
blog/queries.py ONLY. It must not be modified.
"""
from django.test import TestCase
from django.urls import reverse

from blog.models import Author, Category, Comment, Post, Tag


def _seed(db_alias=None):
    """Create a small, deterministic dataset for the front page."""
    tech = Category.objects.create(name="Technology", slug="tech")
    design = Category.objects.create(name="Design", slug="design")

    django_tag = Tag.objects.create(name="Django", slug="django")
    python_tag = Tag.objects.create(name="Python", slug="python")
    web_tag = Tag.objects.create(name="Web", slug="web")

    data = [
        # (title, slug, author_email, category, tags, comments_count)
        ("Getting Started with Django", "gs-django",
         "ana@blog.test", tech, [django_tag, python_tag, web_tag], 5),
        ("Understanding Databases", "db-basics",
         "luis@blog.test", tech, [python_tag, django_tag], 3),
        ("Async Python Deep Dive", "async-python",
         "maria@blog.test", None, [python_tag], 4),
        ("Building REST APIs", "rest-apis",
         "ana@blog.test", tech, [django_tag, web_tag], 2),
        ("Intro to Machine Learning", "intro-ml",
         "carlos@blog.test", None, [python_tag], 6),
        ("CSS Grid Layouts", "css-grid", "elena@blog.test", design, [web_tag], 1),
        ("Scaling PostgreSQL", "pg-scale", "luis@blog.test", tech, [django_tag], 3),
        ("Product Analytics", "product-analytics", "maria@blog.test", design, [web_tag], 2),
    ]

    for idx, (title, slug, email, category, tags, n_comments) in enumerate(data, start=1):
        author, _ = Author.objects.get_or_create(
            name=email.split("@")[0].title(), email=email
        )
        post = Post.objects.create(
            title=title,
            slug=slug,
            author=author,
            category=category,
            body=f"Body of {title}",
            published_at=f"2024-0{idx}-15T10:00:00Z",
            is_published=True,
        )
        post.tags.set(tags)
        for c in range(1, n_comments + 1):
            Comment.objects.create(
                post=post,
                author_name=f"Reader {c}",
                body=f"Comment {c} on {title}",
            )


class FrontPageQueryCountTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _seed()

    def test_front_page_uses_two_queries(self):
        url = reverse("blog:front_page")
        with self.assertNumQueries(2):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
