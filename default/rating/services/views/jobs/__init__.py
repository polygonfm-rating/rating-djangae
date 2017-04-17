#!/usr/bin/python
# -*- coding: utf-8 -*-

import traceback
import logging
import rating.settings
from django.http import HttpResponse
from rating.services.datastore import rating_artist
from rating.services.sources.lastfm import LastFmRatingService
from rating.services.sources.googletrends import GoogleTrendsRatingService
from rating.services.sources.vk import VkRatingService
from rating.services.sources.youtube import YouTubeRatingService
from rating.services.sources.yandex import YandexWordStatRatingService
from rating.services.sources.total import TotalRatingService
from rating.utils import mail
from rating import utils


def run_yandex_wordstat(request):
    return load_rating_task(YandexWordStatRatingService(), "Yandex Wordstat")


def run_vk(request):
    return load_rating_task(VkRatingService(), "VKontakte")


def run_lastfm(request):
    return load_rating_task(LastFmRatingService(), "LastFM")


def run_youtube(request):
    return load_rating_task(YouTubeRatingService(), "YouTube")


def run_google_trends(request):
    return load_rating_task(GoogleTrendsRatingService(), "Google Trends")


def run_total_rating(request):
    calculate_total_rating()
    return HttpResponse("Ok")


def run_check_rating_completed(request):
    total_rating = TotalRatingService()
    if not total_rating.is_today_completed():
        send_not_completed()
    return HttpResponse("Ok")

def load_rating_task(service, service_name):
    try:
        completed, time = service.is_today_completed()
        if not completed:
            artists = rating_artist.query(rating_artist.is_active == True).fetch(batch_size=1000)
            service.fetch_rating_data(artists)
        else:
            logging.info("{}: DO NOTHING. Today's rating data is already collected at {}"
                         .format(service_name, utils.to_moscow(time)))

        calculate_total_rating()
        return HttpResponse("Ok")
    except Exception as e:
        logging.error("{}: FAILED. {}".format(service_name, e))
        mail.send("{}: ошибка при получении данных".format(service_name), traceback.format_exc())
        raise


def calculate_total_rating():
    ratings = [YandexWordStatRatingService(),
               VkRatingService(), #GoogleTrendsRatingService(),
               YouTubeRatingService(), LastFmRatingService()]
    total_rating = TotalRatingService()

    if not total_rating.is_today_completed():
        if all(x.is_today_completed()[0] for x in ratings) and not total_rating.is_today_completed():
            TotalRatingService().calculate(utils.today())
            send_completed()
        else:
            logging.info("TOTAL RATING: Not all rating data is ready to calculate")


def send_not_completed():
    body = rating.settings.URL_BASE
    mail.send("{} Не удалось сформировать рейтинг".format(utils.to_moscow(utils.today())), body, rating.settings.ADMIN_EMAIL_1)


def send_completed():
    body = rating.settings.URL_BASE
    mail.send("{} Рейтинг артистов сформирован".format(utils.to_moscow(utils.today())), body, rating.settings.ADMIN_EMAIL_1)
