#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from rating import utils
from rating.utils import mail


def send_completed(artists_count, time_elapsed):
    sbj = 'Google Trends: данные собраны {}'.format(utils.date_str(datetime.now()))
    body = 'Отчеты Google Trends для {} исполнителей обработаны за {}.'.format(artists_count, time_elapsed)
    mail.send(sbj, body)


def send_error_login(response):
    sbj = 'Google Trends: неуспешный вход в аккаунт'
    body = 'Не удалось войти в аккаунт google для сбора отчетов Google Trends\r\n'
    body += response
    mail.send(sbj, body)


def send_connection_exception(e):
    sbj = 'Google Trends: Connection Exception'
    body = 'Ошибка при получении отчета. '
    body += e.message
    mail.send(sbj, body)

def send_no_report(term, url, response, code):
    sbj = 'Google Trends: неудалось получить отчет для {}'.format(term)
    body = 'Для термина {} не удалось получить отчет Google Trends.'.format(term)
    body += 'URL: {}'.format(url)
    body += 'Response code: {}'.format(code)
    mail.send(sbj, body)
