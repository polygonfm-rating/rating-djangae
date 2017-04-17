#!/usr/bin/python
# -*- coding: utf-8 -*-


from rating.utils import mail
import traceback


def send_error(e):
    body = """
%s

%s
            """ % (e, traceback.format_exc())

    mail.send("Yandex Wordstat: ошибка при получении отчета", body)


def send_not_enough_units():
    body = """
Недостаточно баллов на счете Yandex Direct для получения отчета wordstat.

            """

    mail.send("Yandex Wordstat: недостаточно баллов для получения отчета", body)


def send_report_not_found(artist, term):
    body = """
Не удалось найти отчет wordstat для исполнителя %s, слово %s

            """

    mail.send("Yandex Wordstat: отчет не найден", body)

