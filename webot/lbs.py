# -*- coding: utf-8 -*-
'''
LBS Class for Nook WeBot app.
Support ak (App Key) authentication request ONLY.
已实现封装：
    * Place API
    * IP 定位 API
    * Geocoding API
未实现封装：
    * Place suggestion API
    * Direction API
    * Route Matrix API
    * 坐标转换 API
2014.04.28
Joker Qyou <Joker.Qyou@gmail.com>
'''

import functools
import hashlib
import inspect
import time
import urllib, urllib2

try:
    from django.utils import simplejson
except ImportError, e:
    import json as simplejson


def check_arguments(d):
    '''
    Make sure argument value is not None.
    '''
    for name, value in d.iteritems():
        if value is None:
            raise ValueError, 'paramete %s should not be empty' % name


def checked_arguments(f):
    '''
    A decorator wrapper for using check_arguments.
    '''
    @functools.wraps(f)
    def wrapper(*a, **k):
        d = inspect.getcallargs(f, *a, **k)
        check_arguments(d)
        return f(*a, **k)
    return wrapper


class LBS():
    # v2 place区域检索POI服务
    API_URL_BASE = 'http://api.map.baidu.com'
    POI_SEARCH_API = '/place/v2/search'
    # v2 POI详情服务
    POI_DETAIL_API = '/place/v2/detail'
    # v2 团购信息检索服务
    POI_B2T_SEARCH_API = '/place/v2/eventsearch'
    # v2 商家团购信息查询
    POI_B2T_DETAIL_API = '/place/v2/eventdetail'

    # IP 定位
    IP_LOCATE_API = '/location/ip'

    # Geocoding API
    GEOCODING_API = '/geocoder/v2/'

    APP_KEY, APP_SECRET = None, None

    @checked_arguments
    def __init__(self, app_key = None, app_secret = None):
        self.APP_KEY = app_key
        self.APP_SECRET = app_secret

    def process_result(self, string):
        '''
        Parse string from HTTP response and deal with exceptions.
        '''
        exceptions = {
            1: 'Baidu internal server error', 
            2: 'Invalid request parameters', 
            3: 'Authentication check failed', 
            4: 'Quota check failed', 
            5: 'Invalid app key / App key not found', 
            21: 'Invalid coord `from`', 
            22: 'Invalid coord `to`', 
            24: 'Invalid coord format', 
            25: 'Coords limit exceed', 
            101: 'Service disabled', 
            102: 'Wrong security number / Not in whitelist', 
            202: 'Not authenticated', 
            203: 'Not authenticated', 
            204: 'Not authenticated', 
            205: 'Not authenticated', 
            210: 'Not authenticated', 
            233: 'Not authenticated', 
            231: 'Missing uid or ak (app key)', 
            234: 'Wrong security number signature', 
            210: 'No authentication resource', 
            345: 'Minute quota exceed', 
            346: 'Month quota exceed', 
            347: 'Year quota exceed', 
            348: 'Permanent quota exceed / No authentication', 
            355: 'Day quota exceed', 
            350: 'No quota resource'
        }

        try:
            result = simplejson.loads(string)
        except Exception, e:
            raise Exception, 'JSON parse error'

        if 0 != result['status']:
            if exceptions.has_key(result['status']):
                raise Exception, exceptions[result['status']]
            elif result.has_key('msg'):
                raise Exception, result['msg']
            else:
                raise Exception, 'Unknown exception, status code %d' % result['status']

        return result

    @checked_arguments
    def search_poi_in_radius(self, keyword, radius, location = None, page_num = 0):
        '''
        搜索距离 {location} 半径 {radius} 米范围内关键词为 {keyword} 的感兴趣地点。
        {location}:
            (latitude, longitude)
            纬度和经度
        '''
        location = ','.join([str(coord) for coord in location])
        data = (
            ('query', keyword, ), 
            ('radius', radius, ), 
            ('location', location, ), 
            ('output', 'json', ), 
            ('scope', 2, ), 
            ('page_size', 10, ), 
            ('page_num', page_num, ), 
            ('ak', self.APP_KEY, ), 
        )

        url =  '%s%s?%s' % (
            self.API_URL_BASE, 
            self.POI_SEARCH_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def search_poi_in_city(self, keyword, city = None, page_num = 0):
        '''
        搜索 {city} 城市中关键词为 {keyword} 的感兴趣地点。
        '''
        data = (
            ('query', keyword, ), 
            ('region', city, ), 
            ('output', 'json', ), 
            ('scope', 2, ), 
            ('page_size', 10, ), 
            ('page_num', page_num, ), 
            ('ak', self.APP_KEY, ), 
        )

        url = '%s%s?%S' % (
            self.API_URL_BASE, 
            self.POI_SEARCH_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def search_poi_in_rect(self, keyword, rect = None, page_num = 0):
        '''
        搜索指定矩形 {rect} 范围内关键词为 {keyword} 的感兴趣地点。
        {rect}: 
            (latitude, longitude, latitude, longitude) 
            依次为左下角经纬坐标、右上角经纬坐标。
        '''
        rect = ','.join([str(coord) for coord in rect])
        data = (
            ('query', keyword, ), 
            ('bounds', rect, ), 
            ('output', 'json', ), 
            ('scope', 2, ), 
            ('page_size', 10, ), 
            ('page_num', page_num, ), 
            ('ak', self.APP_KEY, ), 
        )

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.POI_SEARCH_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def query_poi_detail(self, uid):
        '''
        获取 uid 为 {uid} 的感兴趣地点的详情信息。
        '''
        data = (
            ('uid', uid, ), 
            ('output', 'json', ), 
            ('scope', 2, ), 
            ('ak', self.APP_KEY, ), 
        )

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.POI_DETAIL_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    def locate_ip(self, ip = '', coor = None):
        '''
        使用 IP 地址 {ip} 进行定位。
        {coor}:
            值为 None 时返回百度墨卡托坐标，
            值不为 None 时返回百度经纬度坐标。
        '''

        data = [
            ('ip', ip, ), 
            ('ak', self.APP_KEY, ), 
        ]
        if coor is not None:
            data.append(('coor', 'bd09ll', ))

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.IP_LOCATE_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def search_b2t_in_radius(self, keyword, radius, location = None, region = None, event = 'groupon', page_num = 0):
        '''
        查找 {region} 城市中，距离中心点 {location} 距离 {radius} 米范围内
        关键词为 {keyword} 的团购信息。
        {region}:
            城市名，例如：北京市。
        {location}: 
            (latitude, longitude) 中心点经纬度坐标。
        {radius}:
            单位为米。
        '''
        event = 'groupon'
        location = ','.join([str(coord) for coord in location])
        data = (
            ('query', keyword, ), 
            ('event', event, ), 
            ('region', region, ), 
            ('location', location, ), 
            ('radius', radius, ), 
            ('output', 'json', ), 
            ('page_size', 10, ), 
            ('page_num', page_num, ), 
            ('ak', self.APP_KEY, ), 
            ('filter', '', ), 
        )

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.POI_B2T_SEARCH_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def search_b2t_in_rect(self, keyword, rect = None, region = None, event = 'groupon', page_num = 0):
        '''
        查找 {region} 城市中， {rect} 矩形范围内关键词为 {keyword} 的团购信息。
        {region}:
            城市名，例如：北京市。
        {rect}:
            (latitude, longitude, latitude, longitude)
            依次为左下角经纬坐标、右上角经纬坐标。
        '''
        event = 'groupon'
        rect = ','.join([str(coord) for coord in rect])

        data = (
            ('query', keyword, ), 
            ('region', region, ), 
            ('event', 'groupon', ), 
            ('bounds', rect, ), 
            ('page_size', 10, ), 
            ('page_num', page_num, ), 
            ('output', 'json', ), 
            ('ak', self.APP_KEY, ), 
            ('filter', '', ), 
        )

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.POI_B2T_SEARCH_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def query_b2t_detail(self, uid):
        '''
        获取 uid 为 {uid} 的团购事件的详情信息。
        '''
        data = (
            ('uid', uid, ), 
            ('output', 'json', ), 
            ('ak', self.APP_KEY, ), 
        )

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.POI_B2T_DETAIL_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def geocode(self, address, city = ''):
        '''
        对 {city} 城市的地址 {address} 进行地理位置编码，得到经纬度坐标。
        '''
        data = (
            ('address', address, ), 
            ('city', city, ), 
            ('ak', self.APP_KEY, ), 
            ('output', 'json', ), 
        )

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.GEOCODING_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )

    @checked_arguments
    def geodecode(self, location, pois = False, coordtype = 'bd09ll'):
        '''
        对坐标为 {location} 的地点进行逆地理编码，得到该坐标的地址信息。
        {location}:
            (latitude, longitude)
        {pois}:
            是否显示该地址周边的 POI 信息。
        {coordtype}:
            坐标类型，支持：
                `bd09ll` 百度经纬度坐标
                `gcj02ll` 国家测绘局经纬度坐标
                `wgs84ll` WGS84 经纬度坐标（GPS 经纬度坐标）
        '''
        location = ','.join([str(coord) for coord in location])
        data = (
            ('location', location, ), 
            ('pois', int(pois), ), 
            ('coordtype', coordtype, ), 
            ('ak', self.APP_KEY, ), 
            ('output', 'json', ), 
        )

        url = '%s%s?%s' % (
            self.API_URL_BASE, 
            self.GEOCODING_API, 
            urllib.urlencode(data), 
        )

        return self.process_result(
            urllib2.urlopen(url).read()
        )
