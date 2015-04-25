# -*- coding: utf-8 -*-
'''
Models for Blog app.
'''

from django.db import models


class Tag(models.Model):
    text = models.CharField(max_length = 20, unique = True)


class Author(models.Model):
    name = models.CharField(max_length = 20, unique = True)
    email = models.EmailField(unique = True)
    url = models.URLField(blank = True)
    bio = models.CharField(max_length = 300, blank = True)


class Post(models.Model):
    title = models.CharField(max_length = 100)
    content = models.TextField()
    tag = models.ManyToManyField(Tag)
    time = models.DateTimeField()
    author = models.ForeignKey(Author)
    slug = models.CharField(max_length = 100, unique = True)
    # doctype in ['markdown', 'html', 'plaintext']
    doctype = models.CharField(max_length = 20)


class Comment(models.Model):
    post = models.ForeignKey(Post)
    author = models.ForeignKey(Author)
    content = models.TextField()
    time = models.DateTimeField()

    # Fields used to judge spam
    IP = models.IPAddressField()
    UA = models.CharField(max_length = 200)
    spam = models.BooleanField(default = True)
    akismeted = models.BooleanField(default = False)


class Option(models.Model):
    name = models.CharField(max_length = 40, unique = True)
    value = models.CharField(max_length = 100)
    text = models.CharField(max_length = 100)

class QuietEmail(models.Model):
    email = models.EmailField(unique = True)
