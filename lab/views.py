# -*- coding: utf-8 -*-

from django.http import Http404
from django.shortcuts import render_to_response

from nook.settings import STATIC_CDN

PROJECT_KEY_CDN = '//nooks.qiniudn.com/lab/%s/index.html'
PROJECT_KEY_DICT = {
    'cgrid': 'Canvas Grid', 
    'canvas': 'A Canvas Picture Processor', 
    'player': 'A Modified HTML5 Music Player', 
    'yplayer': 'A HTML5 Local Music Player', 
    'clock': 'A HTML5 Canvas Color Clock', 
    'cplayer': 'A Local Video Player in HTML5 Canvas'
}

def project_view(request, project):
    '''
    Render a project page.
    '''
    TEMPLATE = 'lab/project.html'
    try:
        return render_to_response(
            TEMPLATE, 
            {
                'page_title': PROJECT_KEY_DICT[project], 
                'site_name': 'My Nook Lab', 
                'project_url': PROJECT_KEY_CDN % project, 
                'STATIC_CDN': STATIC_CDN
            }
        )
    except Exception, e:
        raise Http404
