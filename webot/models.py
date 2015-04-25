# -*- coding: utf-8 -*-

from django.db import models

class City(models.Model):
    name = models.CharField(max_length = 20, unique = True)
    code = models.CharField(max_length = 20, unique = True)


class User(models.Model):
    open_id = models.CharField(max_length = 255,unique = True)
    subscribe_time = models.DateTimeField()
    admin = models.BooleanField(default = False)
    active = models.BooleanField(default = True)


class Media(models.Model):
    media_id = models.CharField(max_length = 255, unique = True)
    type = models.CharField(max_length = 20)
    by = models.ForeignKey(User)


class Message(models.Model):
    msg_id = models.CharField(max_length = 255, unique = True)
    user = models.ForeignKey(User)
    time = models.DateTimeField()
    type = models.CharField(max_length = 20, default = 'text')
    content = models.TextField()


class POIQuery(models.Model):
    user = models.ForeignKey(User)
    step = models.IntegerField(default = 1)
    input = models.TextField()
    location = models.TextField(blank = True)
    time = models.DateTimeField()
