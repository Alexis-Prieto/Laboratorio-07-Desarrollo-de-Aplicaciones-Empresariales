"""Blog domain models.

Relationships
-------------
Author 1 --- 1 Profile            (OneToOne)
Author 1 --- * Post               (ForeignKey)
Category 1 -- * Post (optional)   (ForeignKey, null=True)
Post * --- * Tag                  (ManyToMany)
Post 1 --- * Comment              (reverse ForeignKey)
"""
from __future__ import annotations

from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Profile(models.Model):
    author = models.OneToOneField(
        Author, related_name="profile", on_delete=models.CASCADE
    )
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"Profile of {self.author.name}"


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(
        Author, related_name="posts", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category,
        related_name="posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    body = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    author_name = models.CharField(max_length=120)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author_name}"
