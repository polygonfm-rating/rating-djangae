#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
from rating.utils import mail
from datetime import timedelta, datetime
from rating import utils
from google.appengine.ext import ndb
from rating.utils import TimeElapsed
from rating.services.datastore import RatingStatus, ServiceStatus


class BaseRatingByDate(object):
    def get_service_name(self):
        return None

    def get_rating_table(self):
        return None

    def get_records_delta(self, record, record_before):
        return None

    def sorted_diff_records(self, diff_data):
        return None

    def get_rating(self, by_date=None):
        date = self.get_completed_date_by_date(by_date) if by_date else self.get_last_completed_date()
        if date is None:
            return ()

        date_before = self.get_completed_date_by_date(date - timedelta(days=1))
        rating = self.get_rating_by_date(date)
        rating_before = self.get_rating_by_date(date_before) if date_before is not None else ()

        diff_data = self.diff_rating_data(rating, rating_before)
        return self.sorted_diff_records(diff_data)

    def get_rating_by_date(self, date):
        query = "SELECT * FROM {} WHERE date=DATETIME('{}')".format(self.get_rating_table(), utils.date_str(date))

        return ndb.gql(query).fetch(batch_size=1000)

    def diff_rating_data(self, rating, rating_before):
        difference = dict()
        before = dict([(record.artist_id, record) for record in rating_before])
        for record in rating:
            if record.artist_id in before:
                difference[record.artist_id] = self.get_records_delta(record, before[record.artist_id])
            else:
                difference[record.artist_id] = record
        return difference.values()

    def get_last_rating(self):
        return self.get_rating()

    def get_last_completed_date(self):
        return RatingServiceStatus.get_last_completed_date(self.get_service_name())

    def get_completed_date_by_date(self, date):
        return RatingServiceStatus.get_completed_by_date(self.get_service_name(), date)


class RatingServiceStatus(object):
    def __init__(self, date=None, service_name=None, state=None):
        if state is None:
            self.state = RatingStatus(service_name=service_name, date=date)
        else:
            self.state = state

    def update(self, status):
        self.state.status = status
        self.state.put()

    def complete(self):
        self.state.status = ServiceStatus.COMPLETED
        self.state.completed_time = utils.datetime_now()
        self.state.put()

    @property
    def date(self):
        return self.state.date

    @staticmethod
    def last_by_status(service_name, service_status):
        result = RatingStatus.query() \
            .filter(RatingStatus.service_name == service_name) \
            .filter(RatingStatus.status == service_status) \
            .order(-RatingStatus.date).fetch(1)

        return result[0] if result else None

    @staticmethod
    def get_last_completed_date(service_name):
        result = RatingStatus.query() \
            .filter(RatingStatus.service_name == service_name) \
            .filter(RatingStatus.status == ServiceStatus.COMPLETED) \
            .order(-RatingStatus.date).fetch(1)

        return result[0].date if result else None

    # TODO remove code duplication
    @staticmethod
    def get_completed_by_date(service_name, date):
        result = RatingStatus.query() \
            .filter(RatingStatus.service_name == service_name) \
            .filter(RatingStatus.status == ServiceStatus.COMPLETED) \
            .filter(RatingStatus.date <= date) \
            .order(-RatingStatus.date).fetch(1)

        return result[0].date if result else None


class BaseRatingService(object):
    def __init__(self):
        self.today = utils.today()
        self.status = None

    def get_service_name(self):
        return None

    def is_today_completed(self):
        completed = self.get_last_state_by_name(ServiceStatus.COMPLETED)
        if completed and completed.date == self.today:
            return True, completed.completed_time
        else:
            return False, None

    def get_last_state_by_name(self, status):
        return RatingServiceStatus.last_by_status(self.get_service_name(), status)

    def set_status_new(self):
        self.status = RatingServiceStatus(service_name=self.get_service_name(), date=self.today)
        self.status.update(ServiceStatus.IN_PROGRESS)

    def set_status_completed(self):
        self.status.complete()

    def set_status(self, last_state):
        self.status = RatingServiceStatus(state=last_state)

    def fetch_rating_data(self, artists_list):
        in_progress = self.get_last_state_by_name(ServiceStatus.IN_PROGRESS)
        if in_progress:
            self.set_status(in_progress)
            self.continue_processing(artists_list)
        else:
            self.start_new_processing(artists_list)

    def start_new_processing(self, artists_list):
        logging.info("{}: START. Total artists count: {}".format(self.get_service_name(), len(artists_list)))
        self.set_status_new()
        self.process_artists(artists_list)

    def get_processed_artists(self, date):
        return None

    def continue_processing(self, artists_list):
        processed = {r.artist_id: None for r in self.get_processed_artists(self.status.date)}
        to_process = list(a for a in artists_list if a.get_id() not in processed)

        logging.info("{}: CONTINUE. Processed artists : {}. Artists to process: {}"
                     .format(self.get_service_name(), len(processed.keys()), len(to_process)))
        self.process_artists(to_process)

    class ProcessingState(object):
        def __init__(self, to_process):
            self.to_process = to_process
            self.__processed = 0

        def add_processed(self, count=1):
            self.__processed += count

        @property
        def processed(self):
            return self.__processed

    def process_artists(self, artists):
        state = BaseRatingService.ProcessingState(len(artists))
        try:
            with TimeElapsed() as t:
                if self.process_artists_int(artists, state):
                    self.set_status_completed()
                    self.send_mail_completed()
                    logging.info("{}: COMPLETED. {} artists retrieved and saved in {}"
                                 .format(self.get_service_name(), len(artists), t.elapsed()))

                else:
                    logging.info("{} STOPPED: Processed {} out of {} artists."
                                 .format(self.get_service_name(), state.processed, state.to_process))

        except Exception as e:
            logging.info(
                "{}: STOPPED. Processed {} out of {} artists."
                    .format(self.get_service_name(), state.processed, state.to_process))
            logging.error("{}: FAILED. {}".format(self.get_service_name(), e))
            raise

    def process_artists_int(self, artists_list, processing_state):
        for a in artists_list:
            service_artist = self.get_service_artist(a)
            self.sleep()
            if service_artist:
                service_artist.put()
                processing_state.add_processed()
        return True

    def get_service_artist(self, artist):
        return None

    def sleep(self):
        pass

    def send_mail_completed(self):
        body = """
            """

        mail.send("{}: данные собраны".format(self.get_service_name()), body)

