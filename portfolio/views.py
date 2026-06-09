from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from portfolio.models import OpenSourceProject
from writing.models import Article, CaseStudy, Series

_CACHE_HOME = 60 * 10   # 10 min


@cache_page(_CACHE_HOME)
@vary_on_headers('Accept-Language')
def home(request):
    case_studies = CaseStudy.objects.filter(is_published=True).order_by('order')[:3]
    articles     = Article.objects.filter(is_published=True).select_related('series')[:5]
    tools        = OpenSourceProject.objects.all()[:2]
    series_list  = Series.objects.all()

    return render(request, 'portfolio/home.html', {
        'case_studies': case_studies,
        'articles':     articles,
        'tools':        tools,
        'series_list':  series_list,
    })
