# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed

from blog.controller import getOptionValue, getHTML
from blog.models import Post

class CorrectMimeFeed(Rss201rev2Feed):
    mime_type = 'application/xml'

    def root_attributes(self):
        attrs = super(CorrectMimeFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs
        
    def add_item_elements(self, handler, item):
        super(CorrectMimeFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])

class RSSFeed(Feed):
    title = getOptionValue('site_name')
    description = getOptionValue('site_description')
    link = getOptionValue('site_url')

    feed_type = CorrectMimeFeed

    def items(self):
        return [
            {
                'title': post.title, 
                'link': '%spost/%s' % (self.link, post.slug), 
                'description': '%s...' % getHTML(post.content)[:50], 
                'content': getHTML(post.content), 
                'pubdate': post.time, 
                'author_name': post.author.name, 
                'guid': '%d' % post.id
            }
            for post in Post.objects.order_by('-time')[:10]
        ]

    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}

    def item_content_encoded(self, item):
        return item['content']

    def item_link(self, item):
        return item['link']

    def item_description(self, item):
        return item['description']

    def item_title(self, item):
        return item['title']

    def item_author_name(self, item):
        return item['author_name']

    def item_pubdate(self, item):
        return item['pubdate']

    def item_guid(self, item):
        return item['guid']


class RSSFeedAll(RSSFeed):
    def items(self):
        return [
            {
                'title': post.title, 
                'link': '%sblog/post/%s' % (self.link, post.slug), 
                'description': '%s...' % getHTML(post.content)[:50], 
                'content': getHTML(post.content), 
                'pubdate': post.time, 
                'author_name': post.author.name, 
                'guid': '%d' % post.id
            }
            for post in Post.objects.order_by('-time')
        ]
