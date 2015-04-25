# -*- coding: utf-8 -*-

import urllib2

from django.utils import simplejson

from api.decorators import *


@render_json
@require_params(('ip', ), method = 'GET')
def api_ip_info(request):
    IP_API_URL = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s'
    try:
        data = urllib2.urlopen(IP_API_URL % request.GET['ip']).read()
        data = simplejson.loads(data)
        return {
            'success': True, 
            'data': data['data']
        }
    except Exception, e:
        return {
            'success': False, 
            'msg': 'Unexpected server error', 
            'data': None
        }


@render_json
def access_deny(request):
    '''
    Deny all access by returning error info.
    '''
    return {
        'success': False, 
        'msg': 'Access denied', 
        'data': None
    }
