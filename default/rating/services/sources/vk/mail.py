#!/usr/bin/python
# -*- coding: utf-8 -*-


from rating.utils import mail
from rating import settings
import urlparse


def send_captcha_required(method_name):
    body = """
Для обработки данных рейтинга из vk.com необходимо ввести код капчи.

%s

VK API method name: %s

Admin
Login: zzz
Password: zzz

            """ % (urlparse.urljoin(settings.URL_BASE, settings.URL_VK_CAPTCHA), method_name)
    mail.send("VKontakte: captcha", body)


def send_vkapi_error(method_name, error):
    body = """
Ошибка при получении данных vk.com

%s

VK API method name: %s
Ошибка:
%s
            """ % (method_name, error.message)

    mail.send("VKontakte: ошибка при получении данных", body)

