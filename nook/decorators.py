# -*- coding: utf-8 -*-

from threading import Thread

from django.http import Http404, HttpResponseServerError, HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson


def render_page(template):
    '''
    Render data to template with given file name.
    '''
    def _render(func):
        def _render_data(request, *args, **kwargs):
            data = func(request, *args, **kwargs)
            if data['status_code'] == 200:
                return render_to_response(template, data)
            elif data['status_code'] == 404:
                raise Http404
            elif data['status_code'] == 503:
                raise HttpResponseServerError
        return _render_data
    return _render


def require_params_4_ajax(params, method = 'get'):
    '''
    Make sure given params exist in request.
    '''
    method = method.upper()
    def _require(func):
        def require(request, *args, **kwargs):
            for param in params:
                if (param not in getattr(request, method))\
                or getattr(request, method)[param].strip() == '':
                    error = {
                        'status_code': 400, 
                        'success': False, 
                        'msg': '%s请求缺少参数，请填写完整的表单' % method
                    }
                    return HttpResponse(
                        simplejson.dumps(error), 
                        mimetype = 'text/json'
                    )
            return HttpResponse(
                simplejson.dumps(
                    func(request, *args, **kwargs)
                ), 
                mimetype = 'text/json'
            )
        return require

    return _require
