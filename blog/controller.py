# -*- coding: utf-8 -*-
'''
Controller for Blog app.
Responsible for all database-related operations.
'''

from datetime import datetime
import hashlib, urllib
import logging
import re

import akismet
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404, HttpResponseServerError
import markdown


from blog.models import *
from nook.settings import EMAIL_ADMIN, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_USE_TLS
from nook.settings import STATIC_CDN, MARK_MORE_SPLIT, AKISMET_API_KEY, AKISMET_PROJECT_UA


# Global vars
PAGE_TAG = 'Page'
RESULT_LIMIT = 10


def getBasicData():
    return {
        'site_url': getOptionValue('site_url'), 
        'site_name': getOptionValue('site_name'), 
        'site_description': getOptionValue('site_description'), 
        'page_links': getPages(), 
        'postprefix': '/blog/post/', 
        'recentposts': getRecentPosts(), 
        'STATIC_CDN': STATIC_CDN
    }


def getPosts(page = 1, perpage = RESULT_LIMIT):
    '''
    Get {page} page of posts, with limit {perpage} posts per page.
    '''
    try:
        start = (page - 1) * perpage
        recentposts = Post.objects.exclude(
            tag__in = [Tag.objects.get(text = PAGE_TAG)]
        ).order_by('-time')[start: start + perpage]
        posts = []
        for recentpost in recentposts:
            tmp = recentpost.__dict__
            tmp.update({'author': recentpost.author.__dict__})
            tmp.update({'comment_count': len(recentpost.comment_set.all())})

            # Translate markdown doc to html doc
            if tmp['doctype'] == 'markdown':
                tmp['content'] = markdown.markdown(
                    tmp['content'], 
                    extensions = ['codehilite', 'extra']
                )

            # Strip content at the 'more' mark
            if len(tmp['content'].split(MARK_MORE_SPLIT)) > 1:
                tmp['content'] = tmp['content'].split(MARK_MORE_SPLIT)[0]
                tmp['more'] = True

            posts.append(tmp)

        return posts
    except Exception, e:
        raise HttpResponseServerError


def getRecentPosts(limit = RESULT_LIMIT):
    '''
    Get the most recent {limit} posts.
    '''
    try:
        return [
            post.__dict__ 
            for post in Post.objects.exclude(
                tag__in = [Tag.objects.get(text = PAGE_TAG)]
            ).order_by('-time')[:limit]
        ]
    except Exception, e:
        return []


def getPager(page = 1, perpage = RESULT_LIMIT):
    '''
    Generate pager for template.
    '''
    try:
        total = len(Post.objects.all().exclude(
            tag__in = [Tag.objects.get(text = PAGE_TAG)])
        )
        if 0 == (total % perpage):
            totalpage = total / perpage
        else:
            totalpage = total / perpage + 1

        if totalpage < page:
            page = totalpage

        if totalpage <= 6 + 1:
            numbers = range(1, totalpage + 1)
        else:
            if page < 1 + 3:
                numbers = range(1, totalpage + 1)[:7]
            elif page > totalpage - 3:
                numbers = range(1, totalpage + 1)[-7:]
            else:
                numbers = range(1, totalpage + 1)[page - 4: page + 3]

        return {
            'prefix': '/blog/page/', 
            'current': page, 
            'total': totalpage, 
            'pages': [{'number': x} for x in numbers]
        }
    except Exception, e:
        return {
            'prefix': '/blog/page/', 
            'current': 1, 
            'total': 1, 
            'pages': []
        }


def getPage(slug):
    '''
    Get page with given slug.
    '''
    try:
        page = Post.objects.get(slug = slug)
        data = page.__dict__
        data.update({'author': page.author.__dict__})

        # Get comments
        comments = page.comment_set.order_by('time')
        comments_dict = []
        for comment in comments:
            tmp = comment.__dict__
            tmp.update({'author': comment.author.__dict__})
            tmp['author']['gravatar'] = getGravatarURL(tmp['author']['email'])
            comments_dict.append(tmp)

        data.update({'comments': comments_dict})

        # Translate markdown doc to html doc
        if data['doctype'] == 'markdown':
            data['content'] = markdown.markdown(
                data['content'], 
                extensions = ['codehilite', 'extra']
            )
        return data
    except Exception, e:
        raise Http404


def getPages():
    '''
    Get pages info.
    '''
    try:
        return [
            {'text': each.title, 'link': each.slug} 
            for each in Post.objects.filter(
                tag__in = [Tag.objects.get(text = PAGE_TAG)]
            )
        ]
    except Exception, e:
        raise []


def getGravatarURL(email):
    '''
    Generate Gravatar image URL for given email.
    '''
    IMAGE_SIZE = 100
    DEFAULT_IMAGE = 'http://www.gravatar.com/avatar'

    gravatar_url = \
        "http://www.gravatar.com/avatar/" \
        + hashlib.md5(email.lower()).hexdigest() \
        + "?"
    gravatar_url += urllib.urlencode({'d':DEFAULT_IMAGE, 's':str(IMAGE_SIZE)})

    return gravatar_url


def getPost(slug):
    '''
    Get post with given slug.
    '''
    try:
        post = Post.objects.get(slug = slug)
        author = post.author.__dict__
        tags = [tag.__dict__ for tag in post.tag.all()]

        # Get comments
        comments = post.comment_set.exclude(spam = True).order_by('time')
        comments_dict = []
        for comment in comments:
            tmp = comment.__dict__
            tmp.update({'author': comment.author.__dict__})
            tmp['author']['gravatar'] = getGravatarURL(tmp['author']['email'])
            comments_dict.append(tmp)

        post = post.__dict__
        post.update({'author': author})
        post.update({'tags': tags})
        post.update({'comments': comments_dict})
        post.update({'description': '%s...' % getPureText(post['content'])[:87]})

        # Translate markdown doc to html doc
        if post['doctype'] == 'markdown':
            post['content'] = markdown.markdown(
                post['content'], 
                extensions = ['codehilite', 'extra']
            )

        return post
    except Exception, e:
        raise Http404


def getOptionValue(key):
    '''
    Get value of given option key.
    '''
    try:
        return Option.objects.get(name = key).value
    except Exception, e:
        raise HttpResponseServerError


def getSearch(keyword):
    '''
    Search for given keyword.
    '''
    try:
        posts = Post.objects\
            .filter(content__contains = keyword)\
            .order_by('-time')[:RESULT_LIMIT]

        results = []

        for post in posts:
            tmp = post.__dict__
            tmp.update({'author': post.author.__dict__})

            # Translate markdown doc to html doc
            tmp['content'] = markdown.markdown(
                tmp['content'], 
                extensions = ['codehilite', 'extra']
            )

            # Strip content at the 'more' mark
            if len(tmp['content'].split(MARK_MORE_SPLIT)) > 1:
                tmp['content'] = tmp['content'].split(MARK_MORE_SPLIT)[0]
                tmp['more'] = True

            results.append(tmp)

        return results
    except Exception, e:
        raise HttpResponseServerError


def getPostsByTag(tagtext):
    '''
    Get posts info by given tag text.
    '''
    try:
        posts = [
            {
                'title': post.title, 
                'slug': post.slug, 
                'author': post.author.__dict__, 
                'time': post.time
            }
            for post in Tag.objects.get(text = tagtext).post_set.all()
        ]
        return posts
    except Exception, e:
        raise HttpResponseServerError


def purifyDict(d):
    '''
    Purify a dict, delete all keys of which their values are not basic types.
    '''
    BASIC_TYPES = (int, str, dict, list, tuple, unicode, )
    for key in d.keys():
        if type(d[key]) not in BASIC_TYPES:
            del d[key]
    return d


def getClientIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def getUserAgent(request):
    try:
        return request.META.get('HTTP_USER_AGENT')
    except Exception, e:
        raise e


def unifyURL(url):
    DEFAULT_PROTOCOL = 'http://'
    if url:
        if url[:7] == 'http://' or url[:8] == 'https://':
            pass
        else:
            url = DEFAULT_PROTOCOL + url
        validate = URLValidator()
        try:
            validate(url)
            return url
        except Exception, e:
            return ''
    else:
        return ''


def insertComment(request):
    '''
    Insert a comment and return it.
    '''
    query = request.POST
    author, new_author = None, None

    try:
        author = Author.objects.get(email = query['email'])
    except Exception, e:
        try:
            new_author = Author(
                name = query['name'], 
                email = query['email'], 
                url = unifyURL(query['url']), 
                bio = ''
            )
            new_author.save()
        except Exception, e:
            error = {
                'success': False, 
                'msg': '您填写的昵称与其他评论者冲突，可能您已经以另一个邮箱地址评论过了。请使用最初填写的邮箱地址。', 
                'status_code': 400
            }
            return error

    if new_author is not None:
        author = new_author

    try:
        post = Post.objects.get(id = int(query['postid']))
    except Exception, e:

        if new_author is not None:
            new_author.delete()

        return {
            'status_code': 400, 
            'success': False, 
            'msg': '请填写所有必需信息'
        }

    try:
        comment = Comment(
            post = post, 
            author = author, 
            content = query['content'].strip(), 
            time = datetime.now(), 
            IP = getClientIP(request), 
            UA = getUserAgent(request)
        )
        comment.save()

        comment_result = purifyDict(comment.__dict__)
        comment_result.update({'author': purifyDict(author.__dict__)})
        return {
            'status_code': 200, 
            'success': True, 
            'msg': '评论成功。您的评论将在1小时内被发往Akismet接受垃圾评论检查，通过后才能显示', 
            'comment': comment_result
        }
    except Exception, e:

        if new_author is not None:
            new_author.delete()

        return {
            'status_code': 500, 
            'success': False, 
            'msg': '保存评论时引发异常。请邮件联系%s。' % EMAIL_ADMIN
        }


def getMentionedEmails(text):
    '''
    Get emails of mentioned comment authors from given comment content.
    '''
    pattern = re.compile(
        ur'@(?P<username>[a-zA-Z0-9\x7f-\xff\u4e00-\u9fa5_\ ]+)\:(\s|$)', 
        re.I
    )
    matches = re.findall(pattern, text)
    names, emails = [each[0] for each in matches], []
    for name in names:
        try:
            emails.append(Author.objects.get(name = name).email.strip())
        except Exception, e:
            pass
    emails = list(set(emails))
    quiet_emails = [each.email for each in QuietEmail.objects.all()]
    [emails.remove(email) for email in emails if email in quiet_emails]
    return emails


def batchEmailNotify(comment):
    '''
    Send comment mention notification to all given emails.
    '''
    from sae.mail import EmailMessage

    emails = getMentionedEmails(comment.content)

    if emails:
        author_name = comment.author.name

        notification = EmailMessage()
        notification.from_addr = u'My Nook 邮件提醒<%s>' % EMAIL_HOST_USER
        notification.to = emails
        notification.subject = u'您在回复中被提及'
        notification.html = u'''<p>您好：<br></p>
<p>您在 %s 对《 %s 》的评论中被提及了。<br></p>
<p> %s 说：“%s”。<br></p>
<p>要回复该评论、查看完整的对话历史，或该文章下的所有评论，请点击此处：<a href="http://nook.sinaapp.com/blog/post/%s" target="_blank">%s</a>。<br></p>
<p>您收到这封邮件，是因为您曾在 Joker Qyou 的博客（ <a href="http://nook.sinaapp.com/blog/" target="_blank">My Nook</a> ）中留下过评论。<br>
如果您不想再收到提醒邮件，请<a href="http://nook.sinaapp.com/blog/mail/" target="_blank">点击此处</a>退订。注意：退订后在博客中的任何评论中被提及，您都不会收到提醒邮件。退订之后您可以在同一页面重新订阅。<br>
注意：此提醒邮件是由博客系统自动发出的，请勿直接回复此邮件。<br></p>
<p>Sincerely    Joker Qyou. <br></p>
''' % (comment.author.name, comment.post.title, comment.author.name, comment.content, comment.post.slug, comment.post.title)
        notification.smtp = (
            EMAIL_HOST, 
            EMAIL_PORT, 
            EMAIL_HOST_USER, 
            EMAIL_HOST_PASSWORD, 
            EMAIL_USE_TLS
        )
        notification.send()


def judgeComments(request):
    '''
    Judge all unchecked comments by Akismet API.
    '''
    unchecked_comments = Comment.objects.filter(akismeted = False)
    spam_checker = akismet.Akismet(agent = AKISMET_PROJECT_UA)
    spam_checker.setAPIKey(
        key = AKISMET_API_KEY, 
        blog_url = 'http://jokerqyou.wordpress.com'
    )
    try:
        keyvalid = spam_checker.verify_key()
    except Exception, e:
        keyvalid = False
    if not keyvalid:
        logging.error('Akismet API key verification failed.')
    else:
        for comment in unchecked_comments:
            try:
                notspam = spam_checker.comment_check(
                    comment.content, 
                    data = {
                        'user_ip': comment.IP, 
                        'user_agent': comment.UA, 
                        'comment_author': comment.author.name, 
                        'comment_author_email': comment.author.email, 
                        'comment_author_url': comment.author.url
                    }
                )
                akismeted = True
            except Exception, e:
                notspam = False
                akismeted = False
            comment.spam = not notspam
            comment.akismeted = akismeted
            if notspam:
                batchEmailNotify(comment)
            comment.save()
    return HttpResponse(
        '%d' % len(unchecked_comments), 
        mimetype = 'text/plain'
    )


def _visible(element):
    from bs4 import Comment as co
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif isinstance(element, co):
        return False
    return True


def getPureText(markdown_text):
    from bs4 import BeautifulSoup
    html = markdown.markdown(markdown_text, extensions = ['extra'])
    return ''.join(filter(_visible, BeautifulSoup(html).findAll(text = True)))


def getHTML(markdown_text):
    '''
    Get HTML content from given markdown content.
    '''
    return markdown.markdown(
        markdown_text, 
        extensions = ['extra', 'codehilite']
    )
