from itertools import groupby

from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from .models import Article, CaseStudy, Series

# Cache timeouts
_CACHE_LIST    = 60 * 10   # 10 min — writing list, archive
_CACHE_ARTICLE = 60 * 60   # 60 min — stable after publish
_CACHE_CS      = 60 * 60   # 60 min — case studies


@cache_page(_CACHE_LIST)
@vary_on_headers('Accept-Language')   # separate cache per locale
def writing_list(request):
    articles    = Article.objects.filter(is_published=True).select_related('series')
    series_list = Series.objects.all()
    return render(request, 'writing/writing_list.html', {
        'articles':    articles,
        'series_list': series_list,
    })


@cache_page(_CACHE_ARTICLE)
@vary_on_headers('Accept-Language')
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)

    same_series = (
        Article.objects
        .filter(series=article.series, is_published=True)
        .exclude(pk=article.pk)
        .select_related('series')[:3]
    )
    if same_series.count() < 3:
        other = (
            Article.objects
            .filter(is_published=True)
            .exclude(pk=article.pk)
            .exclude(series=article.series)
            .select_related('series')[:3 - same_series.count()]
        )
        more_articles = list(same_series) + list(other)
    else:
        more_articles = list(same_series)

    return render(request, 'writing/article_detail.html', {
        'article':       article,
        'more_articles': more_articles,
    })


@cache_page(_CACHE_CS)
@vary_on_headers('Accept-Language')
def case_study_detail(request, slug):
    cs = get_object_or_404(CaseStudy, slug=slug, is_published=True)
    return render(request, 'writing/case_study_detail.html', {'cs': cs})


@cache_page(_CACHE_LIST)
@vary_on_headers('Accept-Language')
def archive(request):
    """All published articles grouped by year → month."""
    articles = (
        Article.objects
        .filter(is_published=True)
        .select_related('series')
        .order_by('-published_at')
    )

    years = []
    for year, year_group in groupby(articles, key=lambda a: a.published_at.year):
        months = []
        for month, month_group in groupby(year_group, key=lambda a: a.published_at.month):
            months.append({'month': month, 'articles': list(month_group)})
        years.append({'year': year, 'months': months})

    return render(request, 'writing/archive.html', {
        'years': years,
        'total': articles.count(),
    })
