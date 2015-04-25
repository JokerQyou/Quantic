# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from blogfeed.views import RSSFeedAll

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'nook.views.home'),
    # Blog
    url(r'^blog/', include('blog.urls')),
    # Site admin
    url(r'^ghost/', include('ghost.urls')),
    # Lab
    url(r'^lab/', include('lab.urls')),
    # XML sitemap (RSS) for Google
    url(r'^sitemap\.xml$', RSSFeedAll()),

    # WeChat robot
    url(r'^webot/', include('webot.urls')),
    # Weibo
    url(r'^weibo/', include('weibo.urls')), 
    # REST APIs
    url(r'^api/', include('api.urls')), 

    # Examples:
    # url(r'^nook/', include('nook.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
