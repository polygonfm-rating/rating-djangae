from operator import attrgetter

from rating.services.datastore import VkRating, VkRatingStatus, ServiceStatus
from rating.services.sources.rating_service import BaseRatingByDate


class VkRatingByDate(BaseRatingByDate):
    def get_service_name(self):
        return None

    def get_rating_table(self):
        return "VkRating"

    def get_records_delta(self, record, record_before):
        return VkRating(artist_id=record.artist_id,
                        date=record.date,
                        tracks_count=record.tracks_count - record_before.tracks_count,
                        in_popular_count=record.in_popular_count,
                        in_interests_count=record.in_interests_count - record_before.in_interests_count)

    def sorted_diff_records(self, diff_data):
        return sorted(diff_data, key=attrgetter('in_popular_count', 'in_interests_count', 'tracks_count'), reverse=True)

    def get_last_completed_date(self):
        result = VkRatingStatus.query(VkRatingStatus.status == ServiceStatus.COMPLETED). \
            order(-VkRatingStatus.date).fetch(1)

        return result[0].date if result else None

    def get_completed_date_by_date(self, date):
        result = VkRatingStatus.query() \
            .filter(VkRatingStatus.status == ServiceStatus.COMPLETED) \
            .filter(VkRatingStatus.date <= date) \
            .order(-VkRatingStatus.date).fetch(1)

        return result[0].date if result else None
