import sys
import itertools
from operator import attrgetter
from rating.services.datastore import GoogleTrendsRating, GoogleTrendsRatingStatus, ServiceStatus
from rating.services.datastore.managers import ArtistManager
from rating import utils


class GoogleTrendsRatingByDate(object):

    def get_rating(self, date=None):
        d = date if date else utils.today()
        result = self._get_nearest_rating(d)
        # move all artists with delta == 0 to the rating end
        for r in itertools.ifilter(lambda x: x.relative_interest_delta == 0, result):
            r.relative_interest_delta = -sys.maxint

        return sorted(result, key=attrgetter('relative_interest_delta'), reverse=True)

    def _get_nearest_rating(self, date):
        artists_count = ArtistManager.active_count()
        result = dict()
        for record in GoogleTrendsRating.query()\
                .filter(GoogleTrendsRating.date <= date) \
                .order(-GoogleTrendsRating.date).fetch(artists_count * 4, batch_size=1000):
            if record.artist_id not in result:
                result[record.artist_id] = record
        return result.values()

    def get_last_completed_date(self):
        result = GoogleTrendsRatingStatus.query() \
            .filter(GoogleTrendsRatingStatus.status == ServiceStatus.COMPLETED) \
            .order(-GoogleTrendsRatingStatus.completed_time).fetch(1)

        return result[0].last_valid_date if result else None

    def __correct_date(self, date):
        last_date = self.get_last_completed_date()
        if date is None or date > last_date:
            return last_date
        return date

        # def get_rating_query(self, date):
        #     return GoogleTrendsRating.query().filter(GoogleTrendsRating.date == date).fetch(batch_size=1000)
        #
        # def get_previous_date(self, date):
        #     return date - timedelta(days=7)
        #
        # def get_completed_date_by_date(self, date):
        #     corrected = utils.week_beginning_by_date(date)
        #     result = GoogleTrendsRatingStatus.query() \
        #         .filter(GoogleTrendsRatingStatus.status == ServiceStatus.COMPLETED) \
        #         .filter(GoogleTrendsRatingStatus.last_week_from == corrected).fetch(1)
        #
        #     return result[0].last_week_from if len(result) == 1 else None
        #
        # def get_last_completed_date(self):
        #     result = GoogleTrendsRatingStatus.query() \
        #         .filter(GoogleTrendsRatingStatus.status == ServiceStatus.COMPLETED) \
        #         .order(-GoogleTrendsRatingStatus.completed_time).fetch(1)
        #
        #     return result[0].last_valid_date if len(result) == 1 else None
        #
        # def get_records_delta(self, record, record_before):
        #     return GoogleTrendsRating(artist_id=record.artist_id,
        #                               artist_name=record.artist_name,
        #                               week_from=record.week_from,
        #                               relative_interest=record.relative_interest - record_before.relative_interest)
        #
        # def sorted_diff_records(self, diff_data):
        #     return sorted(diff_data, key=attrgetter('relative_interest'), reverse=True)
