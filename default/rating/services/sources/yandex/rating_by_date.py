from operator import attrgetter
from rating.services.datastore import YandexWordStatRating
from rating.services.sources.rating_service import BaseRatingByDate
from rating.services.sources.yandex import SERVICE_NAME


class YandexWordStatByDate(BaseRatingByDate):
    def get_service_name(self):
        return SERVICE_NAME

    def get_rating_table(self):
        return "YandexWordStatRating"

    def get_records_delta(self, record, record_before):
        return YandexWordStatRating(artist_id=record.artist_id,
                                    artist_name=record.artist_name,
                                    collecting_date=record.collecting_date,
                                    date=record.date,
                                    shows=record.shows)

    def sorted_diff_records(self, diff_data):
        return sorted(diff_data, key=attrgetter('shows'), reverse=True)
