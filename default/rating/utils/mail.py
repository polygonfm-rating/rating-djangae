#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.api import mail
from rating import settings


def send(sbj, body, cc=None):
    message = mail.EmailMessage()
    message.sender = settings.NO_REPLY_EMAIL
    message.to = settings.ADMIN_EMAIL
    if cc:
        message.cc = cc
    message.subject = "[Рейтинг] {}".format(sbj)
    message.body = body
    message.send()
