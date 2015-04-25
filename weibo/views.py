# -*- coding: utf-8 -*-

import time
import urllib
import urllib2

from django.contrib.auth.decorators import login_required, permission_required
from django.utils import simplejson

from nook.decorators import *
from nook.settings import WEIBO_API_KEY, WEIBO_API_SECRET
from blog.models import Option


@login_required
@permission_required('blog.add_option')
@permission_required('blog.change_option')
@permission_required('blog.delete_option')
@render_page('weibo/auth.html')
def save_auth(request):
    if not 'code' in request.GET:
        return {
            'status_code': 404
        }

    try:
        option = Option.objects.get(name = 'weibo_code')
    except Exception, e:
        option = Option(name = 'weibo_code')

    option.value = request.GET['code']
    option.save()

    AUTH_CALLBACK = 'http://nook.sinaapp.com/weibo/callback/auth'

    API_TOKEN_URL = 'https://api.weibo.com/oauth2/access_token'
    data = (
        ('client_id', WEIBO_API_KEY, ), 
        ('client_secret', WEIBO_API_SECRET, ), 
        ('grant_type', 'authorization_code', ), 
        ('redirect_uri', AUTH_CALLBACK, ), 
        ('code', option.value, ), 
    )
    req = urllib2.Request(API_TOKEN_URL, data = urllib.urlencode(data))
    result = urllib2.urlopen(req).read()
    result = simplejson.loads(result)

    if result.has_key('access_token'):
        try:
            option = Option.objects.get(name = 'weibo_access_token')
            option_expire = Option.objects.get(name = 'weibo_access_expire')
        except Exception, e:
            option = Option(name = 'weibo_access_token')
            option_expire = Option(name = 'weibo_access_expire')

        option.value = result['access_token']
        option_expire.value = int(time.time()) + result['expires_in']

        option.save()
        option_expire.save()
        return {
            'status_code': 200, 
            'script': True
        }
    else:
        return {
            'status_code': 503
        }


def clear_auth(request):
    pass
