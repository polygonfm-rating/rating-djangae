from facade import YouTubeFacade, ChannelStatistics
from rating.services.datastore import YouTubeRating
from rating.services.sources.rating_service import BaseRatingService


class YouTubeRatingService(BaseRatingService):
    _youtube = None

    def __init__(self):
        super(YouTubeRatingService, self).__init__()

    def get_service_name(self):
        return "YouTube"

    def get_youtube(self):
        if not self._youtube:
            self._youtube = YouTubeFacade()
        return self._youtube

    youtube = property(get_youtube)

    def get_service_artist(self, artist):
        stat = self.get_channel_statistics(artist.youtube_user, artist.youtube_channel_id)
        return YouTubeRating(artist_id=artist.get_id(),
                             view_count=stat.view_count,
                             subscriber_count=stat.subscriber_count,
                             date=self.status.date) if stat else None

    def get_channel_statistics(self, user=None, channel_id=None):
        if user:
            return self.youtube.get_channel_statistics(user=user)
        return self.youtube.get_channel_statistics(channel_id=channel_id) if channel_id else None

    def get_processed_artists(self, date):
        return YouTubeRating.query().filter(YouTubeRating.date == date)\
            .fetch(projection=[YouTubeRating.artist_id, ], batch_size=1000)




