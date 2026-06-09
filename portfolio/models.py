from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """
    Singleton model for all editable site-wide content.
    Enforces a single row via save() override.
    Injected into every template via portfolio.context_processors.site_settings.
    """

    # ── Hero ──────────────────────────────────────────────────────────────────
    hero_description   = models.TextField(
        _('hero description'),
        default='I build financial infrastructure and developer tooling.',
    )
    skills_chips       = models.JSONField(
        _('skills chips'), default=list,
        help_text=_('List of skill chip labels shown in the hero, e.g. ["Django · DRF", "Python"].'),
    )
    available_for_work = models.BooleanField(_('available for work'), default=True)
    contact_email      = models.EmailField(_('contact email'), default='sherif@sifusherif.dev')

    # ── About strip ───────────────────────────────────────────────────────────
    about_html = models.TextField(
        _('about text (HTML)'), blank=True,
        help_text=_('HTML for the About section. Use <p> tags. <strong> renders in full ink colour.'),
    )

    # ── Social links ──────────────────────────────────────────────────────────
    github_url   = models.URLField(_('GitHub URL'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    medium_url   = models.URLField(_('Medium URL'), blank=True, default='https://medium.com/@sifusherif')

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_tagline    = models.CharField(
        _('footer tagline'), max_length=200,
        default='Abdulazeez Sherif — Abuja, Nigeria',
    )
    established_year  = models.PositiveSmallIntegerField(_('established year'), default=2026)

    class Meta:
        verbose_name        = _('site settings')
        verbose_name_plural = _('site settings')

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        # Enforce singleton — always save with pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        """Return the singleton instance, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OpenSourceProject(models.Model):
    """An open source tool or book listed in the Tools section."""

    STATUS_BUILDING = 'building'
    STATUS_PLANNED  = 'planned'
    STATUS_LIVE     = 'live'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_BUILDING, _('Building')),
        (STATUS_PLANNED,  _('In progress')),
        (STATUS_LIVE,     _('Live')),
        (STATUS_ARCHIVED, _('Archived')),
    ]

    name        = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    status      = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES)
    tags        = models.JSONField(
        _('tags'), default=list,
        help_text=_('List of tag strings, e.g. ["Python", "Django", "CLI"].'),
    )
    github_url  = models.URLField(_('GitHub URL'), blank=True)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = _('open source project')
        verbose_name_plural = _('open source projects')
        ordering            = ['order']

    def __str__(self):
        return self.name
