# -*- coding: utf-8 -*-
'''
Controller for Ghost app.
'''

from datetime import datetime
import time

from django.core.context_processors import csrf

from blog.controller import getOptionValue
from blog.models import *

from nook.settings import STATIC_CDN
from nook.settings import QINIU_APP_KEY, QINIU_APP_SECRET, QINIU_UPLOAD_BUCKET, QINIU_UPLOAD_CALLBACK

from weibo.controller import get_weibo_auth_url


PERMISSIONS = {
    'auth.add_user': '添加网站用户', 
    'blog.change_option': '修改博客设置', 
    'auth.add_permission': '添加权限', 
    'blog.add_post': '添加博客文章', 
    'sessions.change_session': '修改 Session', 
    'blog.delete_post': '删除博客文章', 
    'sites.delete_site': '删除站点', 
    'auth.delete_permission': '删除权限', 
    'blog.delete_tag': '删除博客标签', 
    'blog.delete_author': '删除博客作者', 
    'blog.delete_comment': '删除博客评论', 
    'sites.change_site': '修改站点', 
    'blog.change_comment': '修改博客评论', 
    'contenttypes.change_contenttype': '', 
    'sessions.delete_session': '删除 Session', 
    'blog.change_author': '修改博客作者信息', 
    'blog.add_option': '添加博客设置选项', 
    'blog.change_tag': '修改博客标签', 
    'auth.add_group': '添加网站用户组', 
    'blog.delete_option': '删除博客设置选项', 
    'contenttypes.delete_contenttype': '', 
    'auth.change_permission': '修改网站用户权限', 
    'blog.add_comment': '添加博客评论', 
    'auth.change_group': '修改网站用户组', 
    'blog.add_tag': '添加博客标签', 
    'blog.add_author': '添加博客作者', 
    'sites.add_site': '添加站点', 
    'sessions.add_session': '添加 Session', 
    'blog.change_post': '修改博客文章内容', 
    'auth.delete_group': '删除网站用户组', 
    'auth.delete_user': '删除网站用户', 
    'auth.change_user': '修改网站用户信息', 
    'contenttypes.add_contenttype': ''
}

PAGE_TAG = 'PAGE'
VERSION_STRING = 'Quantic 0.7 for SAE'


def getPermissions(user):
    '''
    Get readable string of permissions of given user.
    '''
    try:
        perms = list(user.get_all_permissions())
        return set([PERMISSIONS[code_name] for code_name in perms])
    except Exception, e:
        return set([])


def getBasicData():
    return {
        'site_name': getOptionValue('site_name'), 
        'STATIC_CDN': STATIC_CDN
    }


def getSummary(user):
    '''
    Get summary info for given user.
    '''
    try:
        blog_author = Author.objects.get(email = user.email)
        summary = {}
        summary.update(
            {
                'post_number': len(Post.objects.filter(author = blog_author))
            }
        )
        comment_number = 0
        for post in Post.objects.filter(author = blog_author):
            comment_number += len(post.comment_set.all())

        summary.update(
            {
                'comment_number': comment_number
            }
        )
        page_number = len(
            Post.objects.filter(
                author = blog_author, 
                tag__in = [Tag.objects.get(text = PAGE_TAG)]
            )
        )
        tag_number = len(Tag.objects.all())
        approved_comment_number = len(
            Comment.objects.filter(akismeted = True, spam = False)
        )
        pending_comment_number = len(
            Comment.objects.filter(akismeted = False)
        )
        spam_comment_number = len(
            Comment.objects.filter(akismeted = True, spam = True)
        )
        recent_comments = Comment.objects.order_by('-time')[:4]
        summary.update(
            {
                'page_number': page_number, 
                'tag_number': tag_number, 
                'approved_comment_number': approved_comment_number, 
                'pending_comment_number': pending_comment_number, 
                'spam_comment_number': spam_comment_number, 
                'version_string': VERSION_STRING, 
                'recent_comments': recent_comments
            }
        )

        weibo_expire = int(
            Option.objects.get(name = 'weibo_access_expire').value
        )
        if weibo_expire <= int(time.time()):
            weibo_expired = True
        else:
            weibo_expired = False

        summary.update(
            {
                'weibo_expired': weibo_expired
            }
        )
        if weibo_expired:
            summary.update(
                {
                    'weibo_auth_url': get_weibo_auth_url()
                }
            )
        else:
            summary.update(
                {
                    'weibo_expire_time': datetime.fromtimestamp(
                        int(weibo_expire)
                    )
                }
            )

        return summary
    except Exception, e:
        raise e


def getPyTimeByJS(jstime):
    '''
    Get datetime object from given JavaScript time string.
    '''
    _date, _time = \
        jstime.split(' ')[0].split('/'), jstime.split(' ')[1].split(':')
    return datetime(
        int(_date[0]), 
        int(_date[1]), 
        int(_date[2]), 
        int(_time[0]), 
        int(_time[1]), 
        int(_time[2])
    )


def getOptionNames():
    try:
        return [option.name for option in Option.objects.all()]
    except Exception, e:
        return []


def getQiniuToken():
    '''
    Generate Qiniu upload token.
    '''
    # Config app key
    import qiniu.conf
    qiniu.conf.ACCESS_KEY = QINIU_APP_KEY
    qiniu.conf.SECRET_KEY = QINIU_APP_SECRET

    import qiniu.rs
    policy = qiniu.rs.PutPolicy(QINIU_UPLOAD_BUCKET)
    policy.returnUrl = QINIU_UPLOAD_CALLBACK
    policy.returnBody = 'key=$(key)&frame=$(x:framename)'
    policy.expires = 7200

    return {'QINIU_UPLOAD_TOKEN': policy.token()}


def queryString2Dict(s):
    '''
    Transform query string to dict.
    '''
    l, d = s.split('&'), {}
    [
        d.update({each.split('=')[0]: each.split('=')[1].replace('"', '')}) 
        for each in l
    ]
    return d
