# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Login view
    url(r'^$', 'ghost.views.index_view'),
    url(r'^login/$', 'ghost.views.login_view'),
    # Logout view
    url(r'^logout/$', 'ghost.views.logout_view'),
    # New post view
    url(r'^newpost/$', 'ghost.views.newpost_view'),
    # Save a post ( Ajax view )
    url(r'^savepost/$', 'ghost.views.savepost'),
    # Options view
    url(r'^options/$', 'ghost.views.options_view'),
    # Save option values ( Ajax view )
    url(r'^saveoptions/$', 'ghost.views.saveoptions'),
    # Edit a post
    url(r'^editpost/(\d+)/$', 'ghost.views.editpost_view'),
    # Post list view
    url(r'^posts/$', 'ghost.views.posts_view'),
    # Post list view - with page number
    url(r'^posts/page/(\d+)/$', 'ghost.views.posts_view'),
    # Delete a post
    url(r'^deletepost/$', 'ghost.views.delete_post'), 
    # Comment management view
    url(r'^comments/$', 'ghost.views.comments_view'),
    # Comment management view - with page number
    url(r'^comments/page/(\d+)/$', 'ghost.views.comments_view'),
    # Report spam ( Ajax view )
    url(r'^comments/reportspam/$', 'ghost.views.reportspam'),
    # Delete a comment
    url(r'^comments/delete/$', 'ghost.views.deletecomment'), 
    # Qiniu file upload callback
    url(r'^upload/callback/$', 'ghost.views.uploadcallback'),
)
