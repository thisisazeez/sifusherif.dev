from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .utils import render_markdown, word_count_from_html, calculate_read_time


class Series(models.Model):
    """A writing series — e.g. "Django, Actually", "System Design"."""

    name        = models.CharField(_('name'), max_length=100)
    slug        = models.SlugField(unique=True)
    description = models.TextField(_('description'), blank=True)
    # filter_key matches the data-series attribute used by the JS filter on
    # the writing list page: "django" | "system" | "case" | "fintech"
    filter_key  = models.CharField(_('filter key'), max_length=30)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = _('series')
        verbose_name_plural = _('series')
        ordering            = ['order']

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    A writing piece (article, essay, or tutorial).

    Content is authored in Markdown and stored in `body_md`.
    On save, it is rendered to `body_html` automatically.
    Read time and word count are also recalculated on every save.

    Raw HTML blocks are supported inside Markdown, so special template
    components like <div class="art-note"> can be embedded freely.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    title      = models.CharField(_('title'), max_length=300)
    slug       = models.SlugField(unique=True, max_length=320)
    series     = models.ForeignKey(
        Series, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='articles',
        verbose_name=_('series'),
    )

    # ── Hero / eyebrow ────────────────────────────────────────────────────────
    standfirst = models.TextField(
        _('standfirst'),
        help_text=_('One-paragraph summary shown under the title and in the writing list.'),
    )
    assumes    = models.CharField(
        _('assumes'),
        max_length=200, blank=True,
        help_text=_('Prerequisite knowledge shown in the article sidebar.'),
    )
    also_read  = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='referenced_by',
        verbose_name=_('also read'),
        help_text=_('Another article linked in the sidebar.'),
    )

    # ── Content ───────────────────────────────────────────────────────────────
    body_md    = models.TextField(
        _('body (Markdown)'),
        help_text=_(
            'Write in Markdown. Fenced code blocks (```python), tables, and '
            'raw HTML blocks (e.g. <div class="art-note">) are all supported.'
        ),
    )
    body_html  = models.TextField(_('body (HTML)'), blank=True, editable=False)

    # ── Auto-computed metadata ────────────────────────────────────────────────
    word_count = models.PositiveIntegerField(default=0, editable=False)
    read_time  = models.PositiveIntegerField(
        default=0, editable=False,
        help_text=_('Estimated reading time in minutes (auto-calculated).'),
    )

    # ── Publishing ────────────────────────────────────────────────────────────
    published_at  = models.DateField(_('published date'))
    is_published  = models.BooleanField(_('published'), default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    # ── Import tracking ───────────────────────────────────────────────────────
    source_url    = models.URLField(
        _('source URL'), blank=True,
        help_text=_('Original URL if this article was imported from an external platform.'),
    )
    imported_from = models.CharField(
        _('imported from'), max_length=50, blank=True,
        help_text=_('Platform name: "medium", "hashnode", etc. Empty for original content.'),
    )

    class Meta:
        verbose_name        = _('article')
        verbose_name_plural = _('articles')
        ordering            = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Render Markdown → HTML and recalculate metrics on every save
        self.body_html = render_markdown(self.body_md)
        self.word_count = word_count_from_html(self.body_html)
        self.read_time  = calculate_read_time(self.word_count)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('writing:article', kwargs={'slug': self.slug})

    @property
    def published_month_year(self):
        """Returns e.g. "Jun 2026" — used in article eyebrows."""
        return self.published_at.strftime('%b %Y')


class CaseStudy(models.Model):
    """
    A project case study.

    Content is authored in Markdown (same as Article). The meta strip,
    tech tags, and card display properties are all model fields so they
    can be edited in the admin without touching templates.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    number      = models.PositiveSmallIntegerField(
        _('number'),
        help_text=_('Display number: 1 → 001, 2 → 002 …'),
    )
    title       = models.CharField(_('title'), max_length=200)
    slug        = models.SlugField(unique=True)

    # ── Eyebrow (category label on the case study hero) ───────────────────────
    category    = models.CharField(_('category'), max_length=100)       # "Fintech"
    subcategory = models.CharField(_('subcategory'), max_length=100, blank=True)  # "Backend Architecture"

    # ── Hero ──────────────────────────────────────────────────────────────────
    subtitle   = models.TextField(_('subtitle'))
    # Short version shown in the homepage work-grid card
    short_desc = models.TextField(_('short description'))

    # ── Meta strip (4 cells below the hero) ───────────────────────────────────
    role         = models.CharField(_('role'), max_length=200)
    stack        = models.CharField(_('stack'), max_length=200)
    integrations = models.CharField(_('integrations'), max_length=200, blank=True)
    status       = models.CharField(_('status'), max_length=100)

    # ── Homepage work-grid card ────────────────────────────────────────────────
    tech_tags    = models.JSONField(
        _('tech tags'), default=list,
        help_text=_('JSON list of tag strings, e.g. ["Django", "DRF", "PostgreSQL"].'),
    )
    is_dark_card = models.BooleanField(
        _('dark card'), default=False,
        help_text=_('Dark background on the homepage work-grid card (used for SwapFada).'),
    )
    is_wide_card = models.BooleanField(
        _('wide card'), default=False,
        help_text=_('Full-width card spanning both columns (used for Ajo).'),
    )

    # ── Content ───────────────────────────────────────────────────────────────
    body_md   = models.TextField(_('body (Markdown)'))
    body_html = models.TextField(_('body (HTML)'), blank=True, editable=False)

    # ── Navigation ────────────────────────────────────────────────────────────
    next_case_study = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='previous',
        verbose_name=_('next case study'),
    )
    related_article = models.ForeignKey(
        'Article', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('related article'),
        help_text=_('Article linked in the "Read the article" section at the bottom.'),
    )

    # ── Publishing ────────────────────────────────────────────────────────────
    is_published = models.BooleanField(_('published'), default=True)
    order        = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = _('case study')
        verbose_name_plural = _('case studies')
        ordering            = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.body_html = render_markdown(self.body_md)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('writing:case_study', kwargs={'slug': self.slug})

    @property
    def number_display(self):
        """Returns e.g. "001" for number=1."""
        return str(self.number).zfill(3)
