import logging
import mail
from apiclient.discovery import build


class ChannelStatistics:

    def __init__(self, view_count, subscriber_count):
        self.view_count = view_count
        self.subscriber_count = subscriber_count


class YouTubeFacade:
    API_KEY = 'AIzaSyAlMEjxlvSaeVH_ofahtH9aj4c0y1QVw3w'
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    STATISTICS = 'statistics'

    def __init__(self):
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.API_KEY)

    def get_channel_statistics(self, user=None, channel_id=None):
        result = self.youtube.channels().list(part=self.STATISTICS, forUsername=user, id=channel_id).execute()
        if result['items']:
            stat = result['items'][0][self.STATISTICS]
            return ChannelStatistics(int(stat['viewCount']),
                                     int(stat['subscriberCount']))

        mail.send_channel_not_found(channel_id, user)
        logging.error("No Youtube channel with channel-id={} or user={}".format(channel_id, user))
        return None
