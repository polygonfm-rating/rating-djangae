import logging
import datetime
import mail
from google.appengine.ext import ndb
from rating import utils
from requests import ConnectionError
from rating.utils import TimeElapsed
from rating.services.datastore import ServiceStatus, GoogleTrendsRating, GoogleTrendsRatingStatus
from rating.services.sources.rating_service import BaseRatingService

from facade import GoogleTrendsFacade

SERVICE_NAME = "Google Trends"


class GoogleTrendsRatingService(BaseRatingService):
    def __init__(self):
        super(GoogleTrendsRatingService, self).__init__()
        self.trends = GoogleTrendsFacade()
        self.now = utils.datetime_now()
        self.last_dates = []

        # Get report for the last month
        self.date_from = utils.month_ago()

    def get_service_name(self):
        return SERVICE_NAME

    def set_status_new(self):
        self.status = GoogleTrendsRatingStatus(date=self.today, status=ServiceStatus.IN_PROGRESS)
        self.status.put()

    def set_status_completed(self):
        self.status.status = ServiceStatus.COMPLETED
        self.status.completed_time = self.now
        if self.last_dates:
            self.status.last_valid_date = sorted(self.last_dates)[0]
        self.status.put()

    def set_status(self, last_state):
        self.status = last_state

    # TODO merge all service statuses in one manager
    def get_last_state_by_name(self, status):
        result = GoogleTrendsRatingStatus.query() \
            .filter(GoogleTrendsRatingStatus.status == status) \
            .order(-GoogleTrendsRatingStatus.date).fetch(1)
        return result[0] if result else None

    def get_processed_artists(self, date):
        return GoogleTrendsRating.query() \
            .filter(GoogleTrendsRating.collecting_date == date) \
            .fetch(projection=[GoogleTrendsRating.artist_id, ])

    def process_artists_int(self, artists_list, processing_state):
        # TODO try to remove last_dates
        self.last_dates = []
        for a in artists_list:
            term = a.google_trends_term if a.google_trends_term else a.name
            # Report contains relative interest records per each week from selected date
            report = self.trends.get_trends_report(term, date_from=self.date_from)
            logging.info("Get Google Trends report for {}".format(a.name.encode("utf-8")))
            if report:
                self.last_dates.append(self.__save_report(a, report))
                processing_state.add_processed()
            else:
                logging.info("Empty Google Trends report for term {}, artist {}."
                             .format(term.encode('utf-8'), a.name.encode("utf-8")))

            if not self.trends.is_alive:
                return False

        return True

    def __save_report(self, artist, report):
        to_save = []
        sorted_dates = sorted(report.keys(), reverse=True)
        for date in sorted_dates:
            previous_date = date - datetime.timedelta(days=1)
            if previous_date in report:
                delta = report[date] - report[previous_date]

                records = GoogleTrendsRating.query() \
                    .filter(GoogleTrendsRating.artist_id == artist.get_id()) \
                    .filter(GoogleTrendsRating.date == date).fetch()

                if not records:
                    to_save.append(GoogleTrendsRating(artist_id=artist.get_id(),
                                                      artist_name=artist.name,
                                                      collecting_date=self.now,
                                                      relative_interest_delta=delta,
                                                      date=date,
                                                      previous_date=previous_date))
                    logging.info("Record for {}, date {} added".format(artist.name.encode("utf-8"), date))
        ndb.put_multi(to_save)
        return sorted_dates[0]
