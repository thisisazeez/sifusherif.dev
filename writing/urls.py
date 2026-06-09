from django.urls import path
from . import views

urlpatterns = [
    path('',                  views.writing_list,    name='writing_list'),
    path('archive/',          views.archive,         name='archive'),
    path('<slug:slug>/',      views.article_detail,  name='article'),
    path('work/<slug:slug>/', views.case_study_detail, name='case_study'),
]
