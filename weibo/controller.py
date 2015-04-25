# -*- coding: utf-8 -*-

import time
import urllib, urllib2

from django.utils import simplejson
from django.utils.encoding import smart_str

from blog.models import Option
from nook.settings import WEIBO_API_KEY


WEIBO_API_ERRORS = (
    '21315', # Token expired
    '21316', # Token revoked
    '21317', # Token rejected
    '21327', # Expired token
)


def send_weibo(text):
    '''
    Post a new Weibo status.
    '''
    text = smart_str(text[:140])
    API_UPDATE_URL = 'https://api.weibo.com/2/statuses/update.json'
    try:
        access_token = Option.objects.get(name = 'weibo_access_token').value
        access_expire = Option.objects.get(name = 'weibo_access_expire')

    except Exception, e:
        raise Exception, 'Weibo token not found'

    if int(access_expire.value) <= int(time.time()):
        raise Exception, 'Weibo token expired'

    data = (
        (u'access_token', access_token, ), 
        (u'status', text, ), 
    )

    try:
        result = urllib2.urlopen(
            API_UPDATE_URL, 
            data = urllib.urlencode(data)
        ).read()
    except Exception, e:
        raise e

    result = simplejson.loads(result)

    if result.has_key('id'):
        return True
    # If one of these errors occurred, revoke current access token
    elif result.has_key('error_code'):
        if result['error_code'] in WEIBO_API_ERRORS:
            access_expire.value = str(int(time.time()))
            access_expire.save()
        return False

    return False


def get_weibo_auth_url():
    CALLBACK_URL = 'http://nook.sinaapp.com/weibo/callback/auth'
    URL = 'https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s'
    return URL % (WEIBO_API_KEY, CALLBACK_URL)
