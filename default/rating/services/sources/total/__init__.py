import sys
import logging
import itertools
import datetime
from google.appengine.ext import ndb
from operator import attrgetter

from rating import utils
from rating.utils import iter
from rating.services.datastore import TotalRating
from rating.services.datastore.managers import ArtistManager
from rating.services.sources.lastfm.rating_by_date import LastFmRatingByDate
from rating.services.sources.vk.rating_by_date import VkRatingByDate
from rating.services.sources.youtube.rating_by_date import YoutubeRatingByDate
from rating.services.sources.googletrends.rating_by_date import GoogleTrendsRatingByDate
from rating.services.sources.yandex.rating_by_date import YandexWordStatByDate
from formula import TotalRatingFormula


class TotalRatingService(object):
    def __init__(self):
        self.formula = TotalRatingFormula()

    date_from = datetime.date(2016, 5, 1)

    def calculate(self, date):
        self._recalculate(date)

    def is_today_completed(self):
        return TotalRating.query().filter(TotalRating.date == utils.today()).count() > 0

    def get_rating(self, date, is_russian, count):
        if date < self.date_from or date > utils.today():
            return ()

        valid_rating = self._get_valid_rating(date, is_russian, count)

        return {x.position_mixed: x.artist_name for x in valid_rating} if is_russian is None \
            else {x.position: x.artist_name for x in valid_rating}

    def _get_valid_rating(self, date, is_russian, count):
        rating = self._query_rating(date, is_russian, count)
        # if rating version is valid
        if rating and rating[0].formula_version == self.formula.version:
            return rating
        # if today's rating is not ready return rating for the previous day
        elif not rating and date == utils.today():
            return self._get_valid_rating(date - datetime.timedelta(days=1), is_russian, count)

        # calculate rating for the date if rating is empty or not valid
        self._recalculate(date)
        # query valid rating for date
        return self._query_rating(date, is_russian, count)

    def _query_rating(self, date, is_russian, count):
        query = TotalRating.query().filter(TotalRating.date == date)
        if is_russian is None:
            return query.order(TotalRating.position_mixed).fetch(count)
        return query.filter(TotalRating.is_russian == is_russian).order(TotalRating.position).fetch(count)

    def _recalculate(self, date):
        logging.info("TOTAL RATING: START CALCULATION")
        to_save = TotalRatingProcessing(date, self.formula.version).recalculate()
        ndb.put_multi(to_save)
        logging.info("TOTAL RATING: CALCULATED FOR DATE {}".format(date))


class TotalRatingProcessing(object):
    def __init__(self, date, version):
        self.date = date
        self.new_records = []
        self.old_records = None
        self.get_record = None
        self.version = version
        self.total_rating_source = TotalRatingSource(date)

    def recalculate(self):
        self.old_records = TotalRating.query().filter(TotalRating.date == self.date).fetch(batch_size=1000)
        self.get_record = self.old_record if self.old_records else self.new_record

        rus_artists = ArtistManager.active_dict(is_russian=True)
        frg_artists = ArtistManager.active_dict(is_russian=False)
        mxd_artists = iter.merge_dicts(rus_artists, frg_artists)

        self.reload_rating(rus_artists, True)
        self.reload_rating(frg_artists, False)
        self.reload_rating(mxd_artists, None)

        return self.old_records if self.old_records else self.new_records

    def reload_rating(self, artists, is_russian):
        for position, artist in self.total_rating_source.get_rating(artists).iteritems():
            record = self.get_record(artist)
            if record:
                record.formula_version = self.version
                record.artist_name = artists[artist]
                record.date = self.date
                if is_russian is None:
                    record.position_mixed = position
                else:
                    record.is_russian = is_russian
                    record.position = position

    def new_record(self, artist_id):
        r = iter.first(lambda x: x.artist_id == artist_id, self.new_records)
        if r:
            return r
        record = TotalRating(artist_id=artist_id, date=self.date)
        self.new_records.append(record)
        return record

    def old_record(self, artist_id):
        return iter.first(lambda x: x.artist_id == artist_id, self.old_records)


class TotalRatingSource(object):
    class Rating:
        def __init__(self, artist_id):
            self.artist_id = artist_id
            self.vk_rate = 0.0
            self.lastfm_rate = 0.0
            self.youtube_rate = 0.0
            self.yandex_wordstat_rate = 0.0
        #    self.googletrends_rate = 0.0
            self.total_rating = 0.0

        @property
        def sum_rate(self):
            return self.vk_rate + self.lastfm_rate + self.youtube_rate + \
                   self.yandex_wordstat_rate #+ self.googletrends_rate

    def __init__(self, for_date=None):
        self.for_date = for_date
        self._rating_lastfm = None
        self._rating_youtube = None
        self._rating_vk = None
        #self._rating_googletrends = None
        self._yandex_wordstat = None
        self.rating = dict()

    @property
    def rating_lastfm(self):
        if not self._rating_lastfm:
            self._rating_lastfm = LastFmRatingByDate().get_rating(self.for_date)
        return self._rating_lastfm

    @property
    def rating_youtube(self):
        if not self._rating_youtube:
            self._rating_youtube = YoutubeRatingByDate().get_rating(self.for_date)
        return self._rating_youtube

    @property
    def rating_vk(self):
        if not self._rating_vk:
            self._rating_vk = VkRatingByDate().get_rating(self.for_date)
        return self._rating_vk

#    @property
#    def rating_googletrends(self):
#        if not self._rating_googletrends:
#            self._rating_googletrends = GoogleTrendsRatingByDate().get_rating(self.for_date)
#        return self._rating_googletrends

    @property
    def rating_yandex_wordstat(self):
        if not self._yandex_wordstat:
            self._yandex_wordstat = YandexWordStatByDate().get_rating(self.for_date)
        return self._yandex_wordstat

    def get_rating(self, artists):
        self.rating = dict()
        self._add_rating(artists, self.rating_lastfm, "lastfm_rate")
        self._add_rating(artists, self.rating_youtube, "youtube_rate")
        self._add_rating(artists, self.rating_vk, "vk_rate")
        #self._add_rating(artists, self.rating_googletrends, "googletrends_rate")
        self._add_rating(artists, self.rating_yandex_wordstat, "yandex_wordstat_rate")

        t = {position: r.artist_id
             for position, r in enumerate(sorted(self.rating.values(), key=attrgetter("sum_rate")), start=1)}
        return t

    def _add_rating(self, artists, service_rating, attr_name):
        rate = 1
        for record in service_rating:
            if record.artist_id in artists:
                total = self._get_rating_record(record.artist_id)
                setattr(total, attr_name, rate)
                rate += 1

        actual = set(r.artist_id for r in service_rating)
        needed = set(artists.keys())
        for diff in needed.difference(actual):
            logging.warning("Record for artist {} is not found in {}".format(artists[diff].encode('utf-8'), attr_name))
            total = self._get_rating_record(diff)
            setattr(total, attr_name, sys.maxint)

    def _get_rating_record(self, artist_id):
        if artist_id not in self.rating:
            self.rating[artist_id] = TotalRatingSource.Rating(artist_id)
        return self.rating[artist_id]
