from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Article, Series, CaseStudy


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display  = ['name', 'filter_key', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display   = ['title', 'series', 'published_at', 'read_time', 'is_published', 'imported_from']
    list_filter    = ['series', 'is_published', 'imported_from']
    list_editable  = ['is_published']
    search_fields  = ['title', 'standfirst', 'body_md']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['body_html', 'word_count', 'read_time', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'

    fieldsets = [
        (None, {
            'fields': ['title', 'slug', 'series', 'is_published', 'published_at'],
        }),
        (_('Hero'), {
            'fields': ['standfirst', 'assumes', 'also_read'],
        }),
        (_('Content'), {
            'fields': ['body_md'],
            'description': _(
                'Write in Markdown. Use ```python for code blocks. '
                'Use <div class="art-note"><p>…</p></div> for note boxes. '
                'Use <blockquote><p>…</p></blockquote> for pull quotes.'
            ),
        }),
        (_('Computed (read-only)'), {
            'fields': ['body_html', 'word_count', 'read_time'],
            'classes': ['collapse'],
        }),
        (_('Import metadata'), {
            'fields': ['source_url', 'imported_from'],
            'classes': ['collapse'],
        }),
        (_('Timestamps'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse'],
        }),
    ]


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display  = ['number_display', 'title', 'status', 'is_published', 'order']
    list_editable = ['order', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['body_html']

    fieldsets = [
        (None, {
            'fields': ['number', 'title', 'slug', 'is_published', 'order'],
        }),
        (_('Category'), {
            'fields': ['category', 'subcategory'],
        }),
        (_('Hero'), {
            'fields': ['subtitle', 'short_desc'],
        }),
        (_('Meta strip'), {
            'fields': ['role', 'stack', 'integrations', 'status'],
        }),
        (_('Homepage card'), {
            'fields': ['tech_tags', 'is_dark_card', 'is_wide_card'],
        }),
        (_('Content'), {
            'fields': ['body_md'],
        }),
        (_('Navigation'), {
            'fields': ['next_case_study', 'related_article'],
        }),
    ]
