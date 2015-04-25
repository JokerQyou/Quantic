# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns('',

    # Blog home view
    url(r'^$', 'blog.views.home'),

    # Per page view
    url(r'^page/(\d+)/$', 'blog.views.home'),

    # View for specified page
    url(r'^pages/(.+)/$', 'blog.views.page'),

    # View for specified post
    url(r'^post/(.+)/$', 'blog.views.post'),

    # View for blog searching
    url(r'^search/$', 'blog.views.search'),

    # View for read by tag
    url(r'^tag/(.+)/$', 'blog.views.tag'),

    # View for commenting
    url(r'^comment/$', 'blog.views.comment'),

    # Check spam
    url(r'^comment/check/$', 'blog.controller.judgeComments'),

    # Weibo LinkCard API service
    url(r'^linkcard/$', 'blog.views.linkCardAPI'),

    # Email notification subscribe and unsubscribe
    url(r'^mail/$', 'blog.views.subscribe'),

    # Save subscription data
    url(r'^subscribe/$', 'blog.views.save_subscription'),

    # Feed
    url(r'^feed/$', include('blogfeed.urls')),
)
