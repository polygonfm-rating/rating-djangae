import logging
import vk
import time
import mail
from itertools import *
from vk.exceptions import VkAPIError
from rating import utils
from rating.utils import TimeElapsed
from rating.services.datastore import VkRating, VkRatingStatus, ServiceStatus
from rating.services.datastore.managers import VkRatingStatusManager
from rating.services.sources.rating_service import BaseRatingService

AUDIO_SEARCH = "audio.search"
USERS_SEARCH = "users.search"
GET_POPULAR = "execute.get_popular"


class VkRatingService(BaseRatingService):
    # TODO remove somewhere
    ACCESS_TOKEN = '91c1cd1f72a4a7435d8056948826e0a9a85113d02a8354c5fb867c02992572b8dce8f7f0f0446a08915d0'

    def __init__(self):
        super(VkRatingService, self).__init__()
        self.vkapi = vk.api.API(vk.api.Session(self.ACCESS_TOKEN))

    def get_service_name(self):
        return "VKontakte"

    def get_last_state_by_name(self, status):
        return VkRatingStatusManager.last_state_by_status(status)

    def set_status_new(self):
        self.status = VkRatingStatus(date=self.today, status=ServiceStatus.IN_PROGRESS)
        self.status.put()

    def set_status_completed(self):
        self.status.status = ServiceStatus.COMPLETED
        self.status.completed_time = utils.datetime_now()
        self.status.put()

    def set_status(self, last_state):
        self.status = last_state

    def get_processed_artists(self, date):
        return VkRating.query().filter(VkRating.date == date).fetch(projection=[VkRating.artist_id, ])

    def process_artists_int(self, artists_list, processing_state):
        try:
            populars = self.__fetch_popular()
        except VkAPIError as e:
            self.__handle_vkapierror(e, GET_POPULAR)
            return False

        for artist in artists_list:
            name = artist.vk_name if artist.vk_name else artist.name
            try:
                tracks = self.__tracks_count(name)
            except VkAPIError as e:
                self.__handle_vkapierror(e, AUDIO_SEARCH)
                return False

            try:
                in_interests = self.__in_interests_count(name)
            except VkAPIError as e:
                self.__handle_vkapierror(e, USERS_SEARCH)
                return False

            in_popular = self.__in_popular_count(populars, name)
            if in_popular > 0 or tracks > 0 or in_interests > 0:
                a = VkRating(artist_id=artist.get_id(),
                             tracks_count=tracks,
                             in_popular_count=in_popular,
                             in_interests_count=in_interests,
                             date=self.status.date)
                a.put()
                processing_state.add_processed()
        return True

    def __handle_vkapierror(self, e, method_name):
        if e.is_captcha_needed():
            self.__set_captcha(True, e.captcha_sid, e.captcha_img, method_name)
            logging.info("{}: CAPTCHA REQUIRED for {}. Captcha sid: {}, captcha img: {}".
                         format(self.get_service_name(), method_name, e.captcha_sid, e.captcha_img))
            mail.send_captcha_required(method_name)
        else:
            mail.send_vkapi_error(method_name, e)

    def __get_captcha_response(self, method_name):
        if self.status.captcha_required and self.status.captcha_value and self.status.captcha_for_method == method_name:
            return self.status.captcha_sid, self.status.captcha_value
        return None, None

    def __reset_captcha(self):
        self.__set_captcha(False, None, None, None)

    def __set_captcha(self, required, sid, img, method_name):
        self.status.captcha_required = required
        self.status.captcha_sid = sid
        self.status.captcha_img = img
        self.status.captcha_value = None
        self.status.captcha_for_method = method_name
        self.status.put()

    def __fetch_popular(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60000)

        captcha_sid, captcha_value = self.__get_captcha_response(GET_POPULAR)

        with TimeElapsed() as t:
            populars = self.vkapi.execute.get_popular(only_eng=0, captcha_sid=captcha_sid, captcha_key=captcha_value)
            logging.info("{}: Popular artists retrieved from vk.com: {} items in {} sec".
                         format(self.get_service_name(), len(populars), t.elapsed()))
        if captcha_value:
            self.__reset_captcha()
        return populars

    def __in_popular_count(self, populars, artist):
        return sum(1 for _ in ifilter(lambda x: artist.lower() in x.lower(), populars))

    def __tracks_count(self, artist):
        captcha_sid, captcha_value = self.__get_captcha_response(AUDIO_SEARCH)
        result = self.__call_vk_api(lambda:
                                    self.vkapi.audio.search(q=artist, performer_only=1, count=0,
                                                            captcha_sid=captcha_sid,
                                                            captcha_key=captcha_value)[0])
        if captcha_value:
            self.__reset_captcha()
        return result

    def __in_interests_count(self, artist):
        captcha_sid, captcha_value = self.__get_captcha_response(USERS_SEARCH)
        result = self.__call_vk_api(lambda:
                                    self.vkapi.users.search(interests=artist, count=0, v=3.0,
                                                            captcha_sid=captcha_sid,
                                                            captcha_key=captcha_value))
        if captcha_value:
            self.__reset_captcha()
        return result['count'] if 'count' in result else 0

    def __call_vk_api(self, call, retry_count=3, sleep_time=1):
        try:
            time.sleep(0.5)
            return call()
        except VkAPIError as e:
            if e.code == 6 and retry_count > 0:
                logging.exception("{}: Too many requests".format(self.get_service_name()))
                time.sleep(sleep_time)
                return self.__call_vk_api(call, retry_count - 1, sleep_time + 1)
            else:
                logging.exception("{}: API call exception: {}".format(self.get_service_name(), e))
                raise
