from operator import attrgetter
from rating.services.datastore import LastFmRating
from rating.services.sources.rating_service import BaseRatingByDate


class LastFmRatingByDate(BaseRatingByDate):
    def get_service_name(self):
        return "lastFM"

    def get_rating_table(self):
        return "LastFmRating"

    def get_records_delta(self, record, record_before):
        return LastFmRating(artist_id=record.artist_id,
                            date=record.date,
                            listeners_count=record.listeners_count - record_before.listeners_count,
                            plays_count=record.plays_count - record_before.plays_count)

    def sorted_diff_records(self, diff_data):
        return sorted(diff_data, key=attrgetter('plays_count', 'listeners_count'), reverse=True)
