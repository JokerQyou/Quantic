# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from blogfeed.views import RSSFeed#, AtomFeed


urlpatterns = patterns('',

    # Use atom feed as default
    url(r'^$', RSSFeed()),

)
