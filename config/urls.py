from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap

from writing.sitemaps import StaticViewSitemap, ArticleSitemap, CaseStudySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'case_studies': CaseStudySitemap,
}

# Non-localised URLs (admin, static)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
]

# Localised URLs — Django prepends /en/, /ar/ etc.
urlpatterns += i18n_patterns(
    path('', include('portfolio.urls')),
    path('writing/', include(('writing.urls', 'writing'), namespace='writing')),
    prefix_default_language=False,  # English has no prefix: /writing/ not /en/writing/
)
