# -*- coding: utf-8 -*-
'''
Views for Ghost app - the administration system.
'''

from base64 import urlsafe_b64decode
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.utils import simplejson
from django.views.decorators.csrf import ensure_csrf_cookie

import akismet
from blog.models import *
from ghost.controller import *
from nook.decorators import *
from weibo.controller import send_weibo


@ensure_csrf_cookie
def login_view(request):
    '''
    Render the login page and (if login info given) 
    process the authentication.
    '''
    TEMPLATE = 'ghost/login.html'
    if 'name' and 'pass' in request.POST:
        user = authenticate(
            username = request.POST['name'], 
            password = request.POST['pass']
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                data = getBasicData()
                data.update(
                    {
                        'page_title': '登录', 
                        'success': True,
                        'msg': '登录成功，正在跳转……',
                        'status_code': 200
                    }
                )
                return render_to_response(
                    TEMPLATE, 
                    data
                )
            else:
                # disabled account
                data = getBasicData()
                data.update(
                    {
                        'page_title': '登录', 
                        'success': False,
                        'msg': '对不起，这个账户已经被禁用',
                        'status_code': 200
                    }
                )
                return render_to_response(
                    TEMPLATE, 
                    data
                )
        else:
            # login info mismatch
            data = getBasicData()
            data.update(
                {
                    'page_title': '登录', 
                    'success': False,
                    'msg': '登录信息不正确',
                    'status_code': 200
                }
            )
            return render_to_response(
                TEMPLATE, 
                data
            )
    else:
        if not request.user.is_authenticated():
            data = getBasicData()
            data.update(
                {
                    'status_code': 200, 
                    'page_title': '登录'
                }
            )
            data.update(csrf(request))
            return render_to_response(TEMPLATE, data)
        else:
            # redirect for users that already logged in
            return redirect('/ghost/')


@login_required
def logout_view(request):
    '''
    Logout view.
    '''
    logout(request)
    return redirect('/')


@login_required
@render_page('ghost/index.html')
def index_view(request):
    '''
    Summary info about the whole site.
    '''
    data = getBasicData()
    data.update(
        {
            'page_title': '博客信息', 
            'status_code': 200
        }
    )
    user = request.user
    permissions = getPermissions(user)
    # print permissions
    author = Author.objects.get(email = user.email)
    data.update({'summary': getSummary(user)})
    ip_x_forward = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_x_forward:
        ip = ip_x_forward.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    data['summary'].update({'ip_address': ip})
    data.update({'author': author})
    return data

@login_required
@permission_required('blog.add_post')
def newpost_view(request):
    TEMPLATE = 'ghost/newpost.html'
    data = getBasicData()
    data.update(
        {
            'editor': True, 
            'page_title': '添加新文章', 
            'time': datetime.now(), 
            'status_code': 200
        }
    )
    data.update(getQiniuToken())
    data.update(csrf(request))
    return render_to_response(TEMPLATE, data)


@ensure_csrf_cookie
@login_required
@permission_required('blog.add_post')
@permission_required('blog.change_post')
@require_params_4_ajax(('title', 'content', 'time', 'tags',), method = 'post')
def savepost(request):
    '''
    Save a post.
    Notice: this is an Ajax view function.
    Notice: a post without id is a new post, otherwise it's an old post.
    Notice: author parameter is not required, cause it can be queried 
        with `request.user`.
    Notice: slug parameter is optional, title will be used if not provided.
    '''
    DEFAULT_TAG = '默认'
    if 'id' in request.POST:
        # Save an existing post
        try:
            post = Post.objects.get(id = int(request.POST['id']))
            post.title = request.POST['title'].strip()
            post.content = request.POST['content'].strip()
            post.time = getPyTimeByJS(request.POST['time'].strip())
            post.doctype = 'markdown'

            for tag in post.tag.all():
                post.tag.remove(tag)

            for tag in request.POST['tags'].strip().split(','):
                try:
                    _tag = Tag.objects.get(text = tag)
                except Exception, e:
                    _tag = Tag(text = tag)
                    _tag.save()
                post.tag.add(_tag)

            post.save()

            return {'success': True}
        except Exception, e:
            return {'success': False, 'msg': '保存文章时出错'}
    else:
        try:
            post_author = Author.objects.get(email = request.user.email)
            new_post = Post(
                title = request.POST['title'].strip(), 
                content = request.POST['content'].strip(), 
                author = post_author, 
                doctype = 'markdown', 
                time = getPyTimeByJS(request.POST['time'].strip()),
                slug = request.POST['slug'] or request.POST['title'].strip()
            )
            new_post.save()
            new_post.tag.add(Tag.objects.get(text = DEFAULT_TAG))
            for tag in request.POST['tags'].strip().split(','):
                try:
                    _tag = Tag.objects.get(text = tag)
                except Exception, e:
                    _tag = Tag(text = tag)
                    _tag.save()
                new_post.tag.add(_tag)
            new_post.save()

            # Send a new Weibo status
            try:
                _text = u'发表了新文章：《%s》 - My Nook http://nook.sinaapp.com/blog/post/%s' % (new_post.title, new_post.slug)
                send_weibo(_text)
            except Exception, e:
                print e

            return {'success': True}
        except Exception, e:
            return {'success': False, 'msg': '保存文章时出错'}


@login_required
@permission_required('blog.change_option')
def options_view(request):
    '''
    Options view.
    '''
    TEMPLATE = 'ghost/options.html'
    data = getBasicData()
    data.update(
        {
            'page_title': '设置选项', 
            'options': Option.objects.all(), 
            'status_code': 200
        }
    )
    data.update(csrf(request))
    return render_to_response(TEMPLATE, data)


@ensure_csrf_cookie
@login_required
@permission_required('blog.change_option')
@require_params_4_ajax(getOptionNames(), method = 'post')
def saveoptions(request):
    '''
    Save option values.
    Notice: this is a Ajax view.
    '''
    for _name in getOptionNames():
        try:
            option = Option.objects.get(name = _name)
            option.value = request.POST[_name]
            option.save()
        except Exception, e:
            return {
                'success': False, 
                'msg': '保存设置选项值时出错'
            }
    return {'success': True}


@login_required
@permission_required('blog.change_post')
def editpost_view(request, postid):
    '''
    View for editing an existing post.
    '''
    TEMPLATE = 'ghost/newpost.html'
    try:
        data = getBasicData()
        data.update(
            {
                'editor': True, 
                'page_title': '编辑文章', 
                'status_code': 200
            }
        )
        author = Author.objects.get(email = request.user.email)
        post = Post.objects.get(id = int(postid))
        if not post.author.email == author.email:
            return redirect('/ghost/')
        else:
            data.update({'post': post})
            data.update({'tag': post.tag.all()})
            data.update(getQiniuToken())
            data.update(csrf(request))
            return render_to_response(TEMPLATE, data)
    except Exception, e:
        return redirect('/ghost/')


@login_required
@permission_required('blog.change_post')
def posts_view(request, page = 1):
    '''
    Post list view.
    '''
    PAGE_LIMIT = 20
    TEMPLATE = 'ghost/posts.html'
    try:
        page = int(page)
        data = getBasicData()
        data.update(
            {
                'page_title': '文章列表', 
                'status_code': 200
            }
        )
        author = Author.objects.get(email = request.user.email)

        # Pager related
        post_total = len(author.post_set.all())
        post_start = (page - 1) * PAGE_LIMIT
        if 0 == (post_total / PAGE_LIMIT):
            page_total = post_total / PAGE_LIMIT
        else:
            page_total = post_total / PAGE_LIMIT + 1
        pager = {
            'current': page
        }
        if page > 1:
            pager.update({'prev': page - 1})
        if page < page_total:
            pager.update({'next': page + 1})

        posts = [
            {
                'id': post.id, 
                'title': post.title, 
                'time': post.time, 
                'slug': post.slug, 
                'comment_number': len(post.comment_set.all())
            } 
            for post in author.post_set.order_by('-time')[post_start:post_start + PAGE_LIMIT]
        ]
        data.update({'posts': posts})
        data.update({'pager': pager})

        return render_to_response(TEMPLATE, data)
    except Exception, e:
        return redirect('/ghost/')


@login_required
@permission_required('blog.delete_comment')
def comments_view(request, page = 1):
    '''
    View for comments management.
    '''
    PAGE_LIMIT = 20
    TEMPLATE = 'ghost/comments.html'
    try:
        page = int(page)
        data = getBasicData()
        data.update(
            {
                'page_title': '管理评论', 
                'postprefix': '/blog/post/'
            }
        )

        comment_total = len(Comment.objects.all())
        comment_start = (page - 1) * PAGE_LIMIT

        if 0 == (comment_total / PAGE_LIMIT):
            page_total = comment_total / PAGE_LIMIT
        else:
            page_total = comment_total / PAGE_LIMIT + 1
        pager = {
            'current': page
        }
        if page > 1:
            pager.update({'prev': page - 1})
        if page < page_total:
            pager.update({'next': page + 1})

        comments = Comment.objects.order_by('-time')[comment_start:comment_start + PAGE_LIMIT]

        data.update({'pager': pager})
        data.update({'comments': comments})
        return render_to_response(TEMPLATE, data)
    except Exception, e:
        return redirect('/ghost/')


@ensure_csrf_cookie
@login_required
@permission_required('blog.change_comment')
@require_params_4_ajax(('commentid', 'action', ), method = 'post')
def reportspam(request):
    PROJECT_UA = 'My Nook'
    AKISMET_API_KEY = '2eecd33b006f'
    cid = int(request.POST['commentid'])
    try:
        comment = Comment.objects.get(id = cid)
    except Exception, e:
        error = {
            'success': False, 
            'msg': '指定的评论不存在'
        }
        return error
    action = request.POST['action']
    spam_checker = akismet.Akismet(agent = PROJECT_UA)
    spam_checker.setAPIKey(
        key = AKISMET_API_KEY, 
        blog_url = 'http://jokerqyou.wordpress.com'
    )
    if not spam_checker.verify_key():
        error = {
            'success': False, 
            'msg': 'Akismet API key 无效'
        }
        return error
    if (action == 'notaspam') and comment.spam and comment.akismeted:
        comment.spam = False
        comment.save()

        notspam = spam_checker.submit_ham(
            comment.content, 
            data = {
                'user_ip': comment.IP, 
                'user_agent': comment.UA, 
                'comment_author': comment.author.name, 
                'comment_author_email': comment.author.email, 
                'comment_author_url': comment.author.url
            }
        )
        result = {
            'success': True, 
            'msg': '反馈成功，该评论不是垃圾评论'
        }

        import blog.controller as C
        C.batchEmailNotify(comment)
        print 'email fired'

    elif (action == 'itsaspam') and (not comment.spam) and comment.akismeted:
        comment.spam = True
        comment.save()

        aspam = spam_checker.submit_spam(
            comment.content, 
            data = {
                'user_ip': comment.IP, 
                'user_agent': comment.UA, 
                'comment_author': comment.author.name, 
                'comment_author_email': comment.author.email, 
                'comment_author_url': comment.author.url
            }
        )
        result = {
            'success': True, 
            'msg': '反馈成功，该评论是垃圾评论'
        }
    else:
        result = {
            'success': False, 
            'msg': '未知错误，你可能需要刷新页面来查看该评论的最新状态'
        }

    return result


@ensure_csrf_cookie
@login_required
@permission_required('blog.delete_comment')
@require_params_4_ajax(('commentid', 'action', ), method = 'post')
def deletecomment(request):
    '''
    Delete a comment with given id.
    '''
    cid = int(request.POST['commentid'])
    try:
        comment = Comment.objects.get(id = cid)
    except Exception, e:
        error = {
            'success': False, 
            'msg': '指定的评论不存在'
        }
        return error
    if not request.POST['action'] == 'delcomment':
        error = {
            'success': False, 
            'msg': '非法的操作'
        }
        return error
    try:
        author = comment.author
        comment.delete()
        # delete author info if he/she has only one comment
        if len(author.comment_set.all()) <= 1:
            author.delete()
        result = {
            'success': True, 
            'msg': '成功删除指定评论'
        }
        return result
    except Exception, e:
        error = {
            'success': False, 
            'msg': '删除评论时出错'
        }
        return error


@ensure_csrf_cookie
@login_required
@permission_required('blog.delete_post')
@require_params_4_ajax(('postid', ), method = 'post')
def delete_post(request):
    '''
    Delete a post with given id.
    '''
    pid = int(request.POST['postid'])
    try:
        post = Post.objects.get(id = pid)
    except Exception, e:
        error = {
            'success': False, 
            'msg': '指定的文章不存在'
        }
        return error
    try:
        post.delete()
        result = {
            'success': True, 
            'msg': '成功删除指定文章'
        }
        return result
    except Exception, e:
        error = {
            'success': False, 
            'msg': '删除文章时出错'
        }
        return error


def uploadcallback(request):
    '''
    Generate iframe script using upload callback info.
    '''
    result = urlsafe_b64decode(str(request.GET['upload_ret']))
    result = simplejson.dumps(queryString2Dict(result))
    response = '''<script type="text/javascript">window.parent.uploadCallback(%s);</script>''' % result
    return HttpResponse(response, mimetype = 'text/html')

