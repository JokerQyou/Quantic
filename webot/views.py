# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils.encoding import smart_str, smart_unicode
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response

import lbs
from nook.settings import BAIDU_LBS_KEY, BAIDU_LBS_SECRET
from webot.controller import *


@csrf_exempt
def route_view(request):
    '''
    Route specific request to different view functions.
    '''
    if 'get' == request.method.lower():
        # First time to verify URL call by WeChat server
        if verify_signature(request):
            return HttpResponse(
                request.GET.get('echostr', None), 
                mimetype = 'text/plain'
            )
        else:
            return HttpResponse(
                '', 
                mimetype = 'text/plain'
            )
    else:
        if verify_signature(request):
            return HttpResponse(
                passive_response(request), 
                mimetype = 'text/xml'
            )
        else:
            return HttpResponse(
                '', 
                mimetype = 'text/plain'
            )


def passive_response(request):
    '''
    Response based on user's input.
    '''
    msg_input = parse_msg(smart_str(request.body))

    return build_response_by_type(msg_input)


def poi_detail(request, uid):
    '''
    响应 POI 详情查询。
    '''
    TEMPLATE = 'webot/poi_detail.html'
    lbser = lbs.LBS(app_key = BAIDU_LBS_KEY, app_secret = BAIDU_LBS_SECRET)
    try:
        result = lbser.query_poi_detail(uid)
        if result['result'].has_key('telephone'):
            if ',' in result['result']['telephone']:
                result['result']['telephone'] = [
                    each 
                    for each in result['result']['telephone'].split(',')
                    if each.strip() is not None and each.strip() != ''
                ]
            else:
                result['result']['telephone'] = [result['result']['telephone']]
    except Exception, e:
        raise e
        result = {}

    return render_to_response(TEMPLATE, result)
