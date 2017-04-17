#!/usr/bin/python
# -*- coding: utf-8 -*-

from rating.utils import mail


def send_no_artist(artist, details):
    sbj = 'LastFm: нет данных для {}'.format(artist.encode('utf-8'))
    body = """
Не удалось собрать данные исполнителя %s из LastFM.

%s
            """ % (artist.encode('utf-8'), details.encode('utf-8'))

    mail.send(sbj, body)

