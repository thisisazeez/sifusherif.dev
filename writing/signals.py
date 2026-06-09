"""
writing/signals.py

Clears cached pages whenever an Article or CaseStudy is saved in the admin.
This ensures the site stays fresh without manually flushing Redis.

How it works:
  - cache_page() stores responses under keys that include the URL path.
  - make_template_fragment_key() handles fragment caches (if added later).
  - We call cache.clear() here — for a portfolio with a small, stable keyspace
    this is fine. On a larger site you'd target specific cache keys instead.
"""
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Article, CaseStudy


@receiver(post_save, sender=Article)
def clear_article_cache(sender, instance, **kwargs):
    cache.clear()


@receiver(post_save, sender=CaseStudy)
def clear_case_study_cache(sender, instance, **kwargs):
    cache.clear()
