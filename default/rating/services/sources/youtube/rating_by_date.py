from operator import attrgetter
from rating.services.datastore import YouTubeRating
from rating.services.sources.rating_service import BaseRatingByDate


class YoutubeRatingByDate(BaseRatingByDate):
    def get_service_name(self):
        return "YouTube"

    def get_rating_table(self):
        return "YouTubeRating"

    def get_records_delta(self, record, record_before):
        return YouTubeRating(artist_id=record.artist_id,
                             date=record.date,
                             view_count=record.view_count - record_before.view_count,
                             subscriber_count=record.subscriber_count - record_before.subscriber_count)

    def sorted_diff_records(self, diff_data):
        return sorted(diff_data, key=attrgetter('view_count', 'subscriber_count'), reverse=True)
