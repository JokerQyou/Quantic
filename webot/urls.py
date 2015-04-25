# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^robot/$', 'webot.views.route_view'),

    # POI detail page
    url(r'^poi/(.+)/$', 'webot.views.poi_detail'),


    # Examples:
    # url(r'^nook/', include('nook.foo.urls')),

)
