# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Login view
    url(r'^$', 'api.views.access_deny'),
    url(r'^ip/$', 'api.views.api_ip_info'),
)
