"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

'''
# TODO: need to do a better job of dealing with top-level cats
top_level_cats = [
                u'apparel-accessories',
                u'baby-products',
                u'beauty',
                u'electronics',
                u'health-personal-care',
                u'home-garden',
                u'home-improvement',
                u'jewelry',
                u'luggage-bags-travel',
                u'office-products',
                u'pet-supplies',
                u'shoes',
                u'sports-outdoors',
                u'toys-games',
                u'watches'
            ]
top_level_cats_re = '|'.join(top_level_cats)
url(r'^' + top_level_cats_re +'/', views.CategoryListView.as_view(), name='category_view'),
'''

urlpatterns = [
     url(r'^search/', views.SearchListView.as_view(), name='search_view'),
     # url(r'^all-review-topics/', views.CategoryListView.as_view(), name='category_view'),
    url(r'^topics/', views.CategoryListView.as_view(), name='category_view'),
    ]
