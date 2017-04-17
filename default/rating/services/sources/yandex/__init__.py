import logging
import mail
from google.appengine.ext import ndb

from rating.services.datastore import YandexWordStatRating
from rating.utils import iter
from facade import YandexWordStatFacade, YandexWordstatError
from rating.services.sources.rating_service import BaseRatingService

SERVICE_NAME = "Yandex Wordstat"


class YandexWordStatRatingService(BaseRatingService):
    def __init__(self):
        super(YandexWordStatRatingService, self).__init__()
        self.wordstat = YandexWordStatFacade()

    def get_service_name(self):
        return SERVICE_NAME

    def get_processed_artists(self, date):
        return YandexWordStatRating.query().filter(YandexWordStatRating.date == date).fetch(
            projection=[YandexWordStatRating.artist_id, ])

    def process_artists_int(self, artists_list, processing_state):
        try:
            self.wordstat.initialize()
            # todo check chunks
            for chunk in iter.chunks(artists_list, facade.MAX_PHRASES_IN_REPORT_COUNT):
                params = list(artist.get_wordstat_term() for artist in chunk)
                if self.wordstat.is_enough_units(params):
                    items = self._process_report(params, chunk)
                    processing_state.add_processed(len(items))
                else:
                    logging.error("{}: Not enough user units for creating wordstat report.".format(self.get_service_name()))
                    mail.send_not_enough_units()
                    return False
            return True
        except YandexWordstatError as e:
            logging.error("{}: {} ".format(self.get_service_name(), e))
            mail.send_error(e)
            raise

    def _process_report(self, params, artists):
        to_save = []
        report = self.wordstat.get_report(params)
        if report:
            for artist in artists:
                term = artist.get_wordstat_term().lower()
                if term in report:
                    to_save.append(YandexWordStatRating(artist_id=artist.get_id(),
                                                        artist_name=artist.name,
                                                        collecting_date=self.today,
                                                        date=self.today,
                                                        shows=report[term]))
                else:
                    logging.error("{}: wordstat report not returned for artist {}."
                                  .format(self.get_service_name(), artist.name.encode('utf-8')))
                    mail.send_report_not_found(artist.name, term)
            ndb.put_multi(to_save)
        return to_save
