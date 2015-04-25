# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
import time
import urllib, urllib2
import xml.etree.ElementTree as ET

from django.utils.encoding import smart_str
from django.utils import simplejson

from blog.models import *
import lbs
from nook.settings import WEBOT_TOKEN, LTP_API_KEY, BAIDU_LBS_KEY, BAIDU_LBS_SECRET
from webot.models import *


def verify_signature(request):
    '''
    Verify WeChat signature.
    '''
    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce', '')

    param_list = [WEBOT_TOKEN, timestamp, nonce]
    param_list.sort()
    signature_v = hashlib.sha1(''.join(param_list)).hexdigest()

    if signature_v == signature:
        return True
    return False


def parse_msg(msgstr):
    '''
    Parse a msg sent by WeChat server (XML format).
    '''
    msg_xml = ET.fromstring(msgstr)
    msg = {}
    if 'xml' == msg_xml.tag:
        for child in msg_xml:
            msg[child.tag] = smart_str(child.text)

    return msg


def build_text_response(input_msg, text, flag = False):
    '''
    Build text msg in XML format.
    '''
    msg_str = build_multiline_content(
        [
            '<xml>', 
            '<ToUserName><![CDATA[%s]]></ToUserName>', 
            '<FromUserName><![CDATA[%s]]></FromUserName>', 
            '<CreateTime>%d</CreateTime>', 
            '<MsgType><![CDATA[%s]]></MsgType>', 
            '<Content><![CDATA[%s]]></Content>', 
            '<FuncFlag>%d</FuncFlag>', 
            '</xml>'
        ]
    )
    return msg_str % (input_msg['FromUserName'], input_msg['ToUserName'], int(time.time()), 'text', text, int(flag))


def get_msg_type(input_msg):
    '''
    Get message type.
    '''
    return input_msg['MsgType']


def build_response_by_type(input_msg):
    '''
    Build response message by input message type.
    '''
    msg_type = get_msg_type(input_msg)
    # Fill currently
    save_user(input_msg)

    if 'event' == msg_type:
        return build_event_response(input_msg)
    elif 'text' == msg_type:
        save_message(input_msg)
        return deal_with_text(input_msg)
    elif 'location' == msg_type:
        return proceed_poi_search(input_msg)
    elif msg_type in ('image', 'voice', 'video', ):
        save_media(input_msg)
        return build_media_response(input_msg)
    else:
        return build_text_response(
            input_msg, 
            smart_str(
                '抱歉，机器人现在还无法接收此类信息。假以时日，我将会做得更好。'
            )
        )


def _fromUnixCount(count):
    return datetime.fromtimestamp(int(count))


def save_user(input_msg, active = True):
    try:
        user = User.objects.get(open_id = input_msg['FromUserName'])
        user.active = active
        user.save()
    except Exception, e:
        user = User(
            open_id = input_msg['FromUserName'], 
            subscribe_time = _fromUnixCount(input_msg['CreateTime']), 
            active = active
        )
        user.save()
    return user


def save_message(input_msg):
    '''
    Save text message.
    '''
    try:
        try:
            user = User.objects.get(open_id = input_msg['FromUserName'])
        except Exception, e:
            user = save_user(input_msg)

        msg = Message(
            msg_id = input_msg['MsgId'], 
            user = user, 
            type = input_msg['MsgType'], 
            time = _fromUnixCount(input_msg['CreateTime']), 
            content = input_msg['Content']
        )
        msg.save()
        return msg
    except Exception, e:
        print e
        return {}



def save_media(input_msg):
    '''
    Save media.
    '''
    try:
        user_id = input_msg['FromUserName']
        user = User.objects.get(open_id = user_id)
        media = Media(
            media_id = input_msg['MediaId'], 
            type = input_msg['MsgType'], 
            by = user
        )
        media.save()
        if user.admin:
            return build_text_response(
                input_msg, 
                smart_str('报告主人！上传成功～')
            )
        else:
            return build_text_response(
                input_msg, 
                smart_str('谢谢你的支持哦～ o(*^▽^*)o ')
            )
    except Exception, e:
        return build_text_response(
            input_msg, 
            smart_str(
                build_multiline_content(
                    [
                        '抱歉，机器人现在无法接收这个多媒体信息。', 
                        '我会将这条消息报告主人的啦～', 
                        '假以时日，我将会做得更好。'
                    ]
                )
            ), 
            flag = True
        )


def build_event_response(input_msg):
    '''
    Build response to event input.
    '''
    event_type = input_msg['Event']
    if 'subscribe' == event_type:
        save_user(input_msg, active = True)
        return build_text_response(
            input_msg, 
            smart_str(
                build_multiline_content(
                    [
                        '感谢你的关注 ( ￣▽￣)" ', 
                        '输入任意内容可以查看我的能力', 
                        'v(｡･ω･｡)'
                    ]
                )
            )
        )
    elif 'unsubscribe' == event_type:
        save_user(input_msg, active = False)

        return build_text_response(
            input_msg, 
            smart_str(
                '好吧，取关肯定也是经过了深思熟虑的。宇宙很大，生活更大，我们还会见面的。'
            )
        )
    else:
        return build_text_response(
            input_msg, 
            smart_str('呃，你在干什么？')
        )


def build_media_response(input_msg):
    template = build_multiline_content(
        [
            '<xml>', 
            '<ToUserName><![CDATA[%s]]></ToUserName>', 
            '<FromUserName><![CDATA[%s]]></FromUserName>', 
            '<CreateTime>%d</CreateTime>', 
            '<MsgType><![CDATA[%s]]></MsgType>', 
            '%s', 
            '</xml>'
        ]
    )

    TPL = {
        'image': build_multiline_content(
            [
                '<Image>', 
                '<MediaId><![CDATA[%s]]></MediaId>', 
                '</Image>'
            ]
        ),
        'voice': build_multiline_content(
            [
                '<Voice>', 
                '<MediaId><![CDATA[%s]]></MediaId>', 
                '</Voice>'
            ]
        )
    }
    if TPL.has_key(input_msg['MsgType']):
        return template % (
            input_msg['FromUserName'], 
            input_msg['ToUserName'], 
            int(time.time()), 
            input_msg['MsgType'], 
            TPL[input_msg['MsgType']] % input_msg['MediaId']
        )
    return build_text_response(
        input_msg, 
        smart_str('w(ﾟДﾟ)w 你太机智了，我都不知道该说什么了……')
    )
    


def request_ltp(text, options):
    LTP_API_URL = 'http://api.ltp-cloud.com/analysis/'
    post_data = [option for option in options]
    post_data.append(('api_key', LTP_API_KEY, ))
    post_data.append(('text', text, ))

    connection = urllib2.urlopen(
        LTP_API_URL, 
        data = urllib.urlencode(post_data)
    )
    result = connection.read()
    return result


def request_sina_segment(text, tag = True):
    SINA_SEGMENT_API = 'http://segment.sae.sina.com.cn/urlclient.php'
    payload = urllib.urlencode({'context': text})
    args = (
        ('encoding', 'UTF-8', ), 
        ('word_tag', int(tag), ), 
    )
    url = '%s?%s' % (
        SINA_SEGMENT_API, 
        urllib.urlencode(args), 
    )

    return urllib2.urlopen(url, data = payload).read()


def split_content(text):
    result =  request_sina_segment(text, tag = False)
    print request_sina_segment(text)
    data = simplejson.loads(result)
    data.sort(cmp = lambda x, y: int(x['index']) - int(y['index']))
    return ' '.join([each['word'] for each in data])


def split_city(text):
    result = request_ltp(
        text, 
        [
            ('pattern', 'ner', ), 
            ('format', 'plain', ), 
            ('only_ner', 'true')
        ]
    )
    result = result.split('\n')
    lines = [line for line in result if 'Ns' in line]
    cities = [city.replace('Ns', '').strip() for city in lines]

    return cities


def query_weather(cityname):
    WEATHER_API_URL = 'http://mobile.weather.com.cn/data/sk/%s.html?_=%d'
    try:
        try:
            city = City.objects.get(name = cityname)
        except Exception, e:
            result = '⊙▂⊙ 没找到叫“%s”的城市诶……（只能查国内城市哦～）' % cityname
            return result

        req = urllib2.Request(WEATHER_API_URL % (city.code, int(time.time())))
        req.add_header('Referer', 'http://mobile.weather.com.cn/')
        req.add_header('User-Agent', 'Mozilla/5.0 (Linux; Android 4.4.2; XT1032 Build/KXB20.9-1.10-1.24-1.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36')

        result = urllib2.urlopen(req).read()

        weather = simplejson.loads(smart_str(result))['sk_info']
        result = u'%(cityName)s现在温度%(temp)s，%(wd)s%(ws)s，湿度%(sd)s。天气信息发布于%(time)s' % weather
    except Exception, e:
        result = '⊙▂⊙ 查询失败诶……'

    return result


def get_weather(text):
    '''
    Get city from given text and query weather.
    '''
    cities = split_city(text)

    if len(cities) > 1:
        result = '你想查%s的天气？不要太贪心啦～ 一次只能查一个城市哦～' % ('、'.join(cities))
    elif len(cities) == 0:
        result = '不知道你要查哪个城市 ￣o￣ 说清楚点好嘛～'
    else:
        city = ''.join(cities)
        result = query_weather(city)

    return result


def build_multiline_content(l):
    return '\n'.join(l)


def deal_with_text(input_msg):
    SPLITOR, WEATHER = smart_str('分词'), smart_str('的天气')
    POSTS, SEARCHPOST = smart_str('最近文章'), smart_str('搜索文章')
    SEARCHPOI = smart_str('搜索地点')
    content = smart_str(input_msg['Content'])
    if SPLITOR in content:
        content = content.replace(SPLITOR, '')
        if content:
            return build_text_response(input_msg, split_content(content))
        else:
            return build_text_response(
                input_msg, 
                smart_str('("▔□▔) 至少告诉我你要分什么内容啦')
            )
    elif WEATHER in content:
        if content:
            return build_text_response(
                input_msg, 
                smart_str(get_weather(content))
            )
        else:
            return build_text_response(
                input_msg, 
                smart_str('("▔□▔) 至少告诉我你要查哪个城市啦')
            )
    elif POSTS in content:
        return show_latest_posts(input_msg)
    elif SEARCHPOST in content:
        content = content.replace(SEARCHPOST, '').strip()
        return search_posts(input_msg, content)
    elif SEARCHPOI in content:
        content = content.replace(SEARCHPOI, '').strip()
        return search_poi(input_msg, content)
    else:
        return build_text_response(
            input_msg, 
            smart_str(
                build_multiline_content(
                    [
                        '_(:з」∠)_ 五月病发作中…… 偶遇服务器偷懒请大家多包涵', 
                        '现在可用的功能有：', 
                        '0、分词/断句：句子前/后带“分词”即可', 
                        '1、查当前天气：输入“XX的天气”', 
                        '2、输入“搜索地点 XXX@n”搜索你周边n米内关键词为XXX的地点(如“搜索地点饭店@200”搜索200米内的饭店)', 
                        '3、输入“最近文章”查看主人博客最近的文章', 
                        '4、输入“搜索文章 XXX”搜索主人的博客文章', 
                        'v(｡･ω･｡)'
                    ]
                )
            )
        )


def build_news_response(input_msg, news, flag = False):
    '''
    Build news response to input_msg user.
    '''
    item_template = build_multiline_content(
        [
            '<item>', 
            '<Title><![CDATA[%(title)s]]></Title> ', 
            '<Description><![CDATA[]]></Description>', 
            '<PicUrl><![CDATA[%(pic)s]]></PicUrl>', 
            '<Url><![CDATA[%(url)s]]></Url>', 
            '</item>'
        ]
    )

    
    news_content = ''''''

    for news_item in news:
        news_content += item_template % news_item

    template = build_multiline_content(
        [
            '<xml>', 
            '<ToUserName><![CDATA[%s]]></ToUserName>', 
            '<FromUserName><![CDATA[%s]]></FromUserName>', 
            '<CreateTime>%d</CreateTime>', 
            '<MsgType><![CDATA[news]]></MsgType>', 
            '<ArticleCount>%d</ArticleCount>', 
            '<Articles>', 
            '%s', 
            '</Articles>', 
            '<FuncFlag>%d</FuncFlag>', 
            '</xml>'
        ]
    )

    return template % (input_msg['FromUserName'], input_msg['ToUserName'], int(time.time()), len(news), news_content, int(flag))


def _is_empty(l):
    for i in l:
        if i is None or i == '':
            return True

    return False


def search_poi(input_msg, content):
    '''
    Step 1 of searching POI.
    '''
    try:
        user = User.objects.get(open_id = input_msg['FromUserName'])
    except Exception, e:
        user = save_user(input_msg)

    input_data = [each.strip() for each in content.split('@')]
    if len(input_data) != 2 or _is_empty(input_data):
        return build_text_response(
            input_msg, 
            smart_str(
                build_multiline_content(
                    [
                        '⊙▂⊙ 格式不对哦…… 输入“搜索地点XX@n”', 
                        '搜索附近n米范围内关于XX的地点'
                    ]
                )
            )
        )

    try:
        poi_state = POIQuery(
            user = user, 
            input = content, 
            step = 1, 
            time = _fromUnixCount(input_msg['CreateTime'])
        )
        poi_state.save()

        return build_text_response(
            input_msg, 
            smart_str(
                build_multiline_content(
                    [
                        'Okay. 下面请发送你的地理位置。', 
                        '在微信输入框右边的“+”按钮，展开点击地理位置，选择最接近你的位置，发送。'
                    ]
                )
            )
        )
    except Exception, e:
        return build_text_response(
            input_msg, 
            smart_str('⊙▂⊙ 服务器开小差了……'), 
            flag = True
        )


def proceed_poi_search(input_msg):
    try:
        user = User.objects.get(open_id = input_msg['FromUserName'])
    except Exception, e:
        user = save_user(input_msg)

    try:
        poi_state = POIQuery.objects.get(
            user = user, 
            step = 1
        )
        location = (
            float(input_msg['Location_X']), 
            float(input_msg['Location_Y']), 
        )
        input_data = [each.strip() for each in poi_state.input.split('@')]

        lbser = lbs.LBS(
            app_key = BAIDU_LBS_KEY, 
            app_secret = BAIDU_LBS_SECRET
        )

        result = lbser.search_poi_in_radius(
            smart_str(input_data[0]), 
            int(input_data[1]), 
            location = location
        )
        poi_state.location = ','.join(
            (input_msg['Location_X'], input_msg['Location_Y'], )
        )
        poi_state.step = 0
        poi_state.save()
        if result['total'] < 1:
            return build_text_response(
                input_msg, 
                smart_str('(>_<) 没有搜索到…… 请尝试扩大范围或更换关键词')
            )
        else:
            news = [
                {
                    'title': '\n'.join((each['name'], each['address'], )), 
                    'pic': '', 
                    'url': 'http://nook.sinaapp.com/webot/poi/%s' % each['uid']
                }
                for each in result['results']
            ]
            return build_news_response(
                input_msg, 
                news
            )
    except Exception, e:
        return build_text_response(
            input_msg, 
            smart_str('呃，你在干什么？')
        )


def show_latest_posts(input_msg, limit = 5):
    '''
    Show latest {limit} posts of my blog.
    '''
    try:
        posts = Post.objects.order_by('-time')[:limit]
        news = [
            {
                'title': post.title, 
                'pic': 'http://nook.sinaapp.com/static/favicon.png', 
                'url': 'http://nook.sinaapp.com/blog/post/%s' % post.slug
            } 
            for post in posts
        ]

        if len(news) == 0:
            return build_text_response(
                input_msg, 
                smart_str('⊙▂⊙ 没找到结果呃……'), 
                flag = True
            )

        return build_news_response(input_msg, news)
    except Exception, e:
        return build_text_response(
            input_msg, 
            smart_str('⊙▂⊙ 服务器开小差了……'), 
            flag = True
        )


def search_posts(input_msg, content):
    '''
    Search for posts.
    '''
    limit = 10
    try:
        posts = Post.objects.filter(
            content__contains = content
        ).order_by('-time')[:limit]

        news = [
            {
                'title': post.title, 
                'pic': 'http://nook.sinaapp.com/static/favicon.png', 
                'url': 'http://nook.sinaapp.com/blog/post/%s' % post.slug
            }
            for post in posts
        ]

        if len(news) == 0:
            return build_text_response(
                input_msg, 
                smart_str('⊙▂⊙ 没找到结果呃……'), 
                flag = True
            )

        return build_news_response(input_msg, news)
    except Exception, e:
        return build_text_response(
            input_msg, 
            smart_str('⊙▂⊙ 服务器开小差了……'), 
            flag = True
        )
