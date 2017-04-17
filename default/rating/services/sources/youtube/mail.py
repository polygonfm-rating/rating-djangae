#!/usr/bin/python
# -*- coding: utf-8 -*-

from rating.utils import mail


def send_channel_not_found(channel_id, user):
    sbj = 'YouTube: нет канала ({}, {})'.format(channel_id, user)
    body = 'Не удалось найти канал YouTube для id = {}, username = {}.'.format(channel_id, user)
    mail.send(sbj, body)
