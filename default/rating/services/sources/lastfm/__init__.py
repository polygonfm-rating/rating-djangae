import logging
import time

import mail
import pylast
from rating.services.datastore import LastFmRating
from rating.services.sources.rating_service import BaseRatingService


class LastFmRatingService(BaseRatingService):
    API_KEY = "789d3fcf59778f1491416531823a391e"
    API_SECRET = "cf79c31ece3219938097ea946275e9fb"

    def __init__(self):
        super(LastFmRatingService, self).__init__()
        self.lastfm = pylast.LastFMNetwork(api_key=self.API_KEY, api_secret=self.API_SECRET)

    def get_service_name(self):
        return "lastFM"

    def get_rating_table(self):
        return "LastFmRating"

    def get_service_artist(self, artist):
        lfm_artist = self.lastfm.get_artist(artist.name)
        try:
            plays, listeners = lfm_artist.get_playcount_and_listeners()

            return LastFmRating(artist_id=artist.get_id(),
                                listeners_count=listeners,
                                plays_count=plays,
                                date=self.status.date)
        except pylast.WSError as e:
            # just skip artist
            logging.info(u'lastFm: Error while processing artist with name {}: {}'.format(artist.name, e.details))
            mail.send_no_artist(artist.name, e.details)
            return None

    def get_processed_artists(self, date):
        return LastFmRating.query().filter(LastFmRating.date == date)\
            .fetch(projection=[LastFmRating.artist_id, ], batch_size=1000)

    def sleep(self):
        time.sleep(0.3)
