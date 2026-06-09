from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

# Non-localised URLs (admin, static)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Localised URLs — Django prepends /en/, /ar/ etc.
urlpatterns += i18n_patterns(
    path('', include('portfolio.urls')),
    path('writing/', include(('writing.urls', 'writing'), namespace='writing')),
    prefix_default_language=False,  # English has no prefix: /writing/ not /en/writing/
)
