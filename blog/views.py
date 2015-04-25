# -*- coding: utf-8 -*-
'''
View functions for Blog app.
Responsible for all page view rendering.
'''

from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie

import markdown

from blog.controller import *
from blog.models import *
from nook.decorators import *


@render_page('blog/home.html')
def home(request, page = 1):
    '''
    Home page view for blog.
    '''
    try:
        data = getBasicData()
        data.update(
            {
                'page_title': 'Home', 
                'posts': getPosts(page = int(page)), 
                'pager': getPager(page = int(page)), 
                'status_code': 200
            }
        )
        return data
    except Exception, e:
        return {
            'status_code': 503
        }


@render_page('blog/post.html')
def page(request, slug):
    '''
    Page view for given slug.
    '''
    try:
        page = getPage(slug)
        page_links = getPages()

        for page_link in page_links:
            if page_link['text'].lower() == page['title']:
                page_link['current'] = True

        page.update(getBasicData())
        page.update(
            {
                'page_title': page['title'], 
                'status_code': 200
            }
        )
        page.update(csrf(request))
        return page
    except Exception, e:
        return {
            'status_code': 404
        }


@render_page('blog/post.html')
def post(request, slug):
    '''
    Post view for given slug.
    '''
    try:
        data = getPost(slug)

        data.update(getBasicData())
        data.update(
            {
                'page_title': data['title'],
                'status_code': 200
            }
        )
        data.update(csrf(request))
        return data
    except Exception, e:
        return {
            'status_code': 404
        }


@render_page('blog/search.html')
def search(request):
    '''
    Search for result.
    '''
    SEARCH_PARAM = 'keyword'
    if SEARCH_PARAM in request.GET:
        keyword = request.GET[SEARCH_PARAM].strip()
        if keyword:
            data = getBasicData()
            data.update(
                {
                    'page_title': 'Search results for %s' % keyword, 
                    'posts': getSearch(keyword), 
                    'status_code': 200
                }
            )
            return data
        else:
            return {
                'status_code': 404
            }
    else:
        return {
            'status_code': 404
        }


@render_page('blog/tag.html')
def tag(request, text):
    '''
    View for given tag text.
    '''
    tagtext = text.strip()
    try:
        data = getBasicData()
        data.update(
            {
                'page_title': 'Posts tagged %s' % tagtext, 
                'tag': tagtext, 
                'posts': getPostsByTag(tagtext), 
                'status_code': 200
            }
        )
        return data
    except Exception, e:
        return {
            'status_code': 404
        }


# URL is not required for Author
@ensure_csrf_cookie
@require_params_4_ajax(('name', 'email', 'content'), method = 'post')
def comment(request):
    '''
    Process commenting request.
    '''
    return {
            'status_code': 400, 
            'success': False, 
            'msg': '垃圾评论泛滥，所有文章评论暂时关闭'
        }
    # return insertComment(request)


@render_page('blog/mail.html')
def subscribe(request):
    '''
    View for subscribing / unsubscribing email notification.
    '''
    data = getBasicData()
    data.update(
        {
            'page_title': '评论回复提醒退订/订阅', 
            'status_code': 200
        }
    )
    data.update(csrf(request))
    return data


@ensure_csrf_cookie
@require_params_4_ajax(('email', ), method = 'post')
def save_subscription(request):
    '''
    Subscribe or unsubscribe email notification.
    '''
    data = {'status_code': 200}
    email = request.POST['email']
    if not email.strip():
        error = {
            'success': False, 
            'msg': '请填写您的 Email 地址'
        }
        return error
    try:
        q = QuietEmail.objects.get(email = email)
        subscribe = True
    except Exception, e:
        subscribe = False
    if subscribe:
        try:
            q = QuietEmail.objects.get(email = email)
            q.delete()
            data.update({'success': True})
        except Exception, e:
            data.update({'success': False, 'msg': '你已经订阅了评论回复提醒邮件'})
    else:
        try:
            q = QuietEmail(email = email)
            q.save()
            data.update({'success': True})
        except Exception, e:
            data.update({'success': False, 'msg': '您已经退订了评论回复提醒邮件'})
    return data


def linkCardAPI(request):
    '''
    Generate Weibo LinkCard JSON content.
    Notice: require `url` GET parameter.
    '''
    from django.utils import simplejson

    key = 'url'
    if not key in request.GET:
        error = simplejson.dumps({})
        return HttpResponse(error, mimetype = 'text/json')
    else:
        url = request.GET[key]
        slug = url\
            .replace('http://nook.sinaapp.com/blog/post/', '')\
            .replace('/', '')
        try:
            post = Post.objects.get(slug = slug)
            data = {
                'object_type': 'webpage', 
                'display_name': post.title, 
                'links': {
                    'url': 'http://nook.sinaapp.com/blog/post/%s' % post.slug, 
                    'display_name': '查看全文'
                }, 
                'author': {
                    'url': '', 
                    'object_type': 'person', 
                    'display_name': post.author.name
                }, 
                'url': 'http://nook.sinaapp.com/blog/post/%s' % post.slug, 
                'image': {
                    'url': 'http://nookstatic.qiniudn.com/staticfavicon.png'
                }, 
                'full_image': {
                    'url': 'http://nookstatic.qiniudn.com/staticfavicon.png'
                }, 
                'create_at': post.time.strftime('%Y年%m月%d日'), 
                'summary': '%s...' % getPureText(post.content)[:87]
            }
        except Exception, e:
            data = {}
        data = simplejson.dumps(data)
        return HttpResponse(data, mimetype = 'text/json')
