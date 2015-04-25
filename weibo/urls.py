# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns('',

    # Weibo auth callback
    url(r'^callback/auth/$', 'weibo.views.save_auth'), 
    # Weibo unauth callback
    url(r'^callback/unauth/$', 'weibo.views.clear_auth'), 

)
