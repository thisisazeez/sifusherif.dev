from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, CaseStudy


class StaticViewSitemap(Sitemap):
    """Sitemap for main static/index pages."""
    priority = 0.8
    changefreq = 'daily'
    i18n = True

    def items(self):
        return ['home', 'writing:writing_list', 'writing:archive']

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    """Sitemap for all published articles."""
    priority = 0.9
    changefreq = 'weekly'
    i18n = True

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class CaseStudySitemap(Sitemap):
    """Sitemap for all published case studies."""
    priority = 1.0
    changefreq = 'monthly'
    i18n = True

    def items(self):
        return CaseStudy.objects.filter(is_published=True)
