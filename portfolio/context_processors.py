from portfolio.models import SiteSettings


def site_settings(request):
    """Inject SiteSettings into every template context."""
    return {'site': SiteSettings.get()}
