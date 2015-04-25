# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response

from nook.decorators import *


# Global consts
PROJECT_NAME = 'My Nook'


@render_page('home.html')
def home(request):
    return {
        'project_name': PROJECT_NAME, 
        'status_code': 200
        }
