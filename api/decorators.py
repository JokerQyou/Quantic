# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson


def render_json(func):
    '''
    Render JSON data for given function.
    '''
    def _render(*args, **kwargs):
        return HttpResponse(
            simplejson.dumps(func(*args, **kwargs)), 
            mimetype = 'text/json'
        )
    return _render


def require_params(params, method = 'GET'):
    method = method.upper()
    def _check(func):
        def _require(*args, **kwargs):
            request = args[0]
            for param in params:
                if not param in getattr(request, method) \
                or getattr(request, method)[param].strip() == '':
                    return {
                        'success': False, 
                        'msg': 'Missing %s parameter: %s' % (method, param), 
                        'data': None
                    }
            return func(*args, **kwargs)
        return _require
    return _check
