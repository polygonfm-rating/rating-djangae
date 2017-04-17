from google.appengine.ext import ndb
from rating.services.datastore import ServiceStatus, VkRatingStatus, rating_artist


class ArtistManager(object):
    @staticmethod
    def active(is_russian=None):
        query = "SELECT name FROM rating_artist WHERE is_active=True"
        if is_russian is not None:
            query += " AND is_russian={} ".format(is_russian)

        return ndb.gql(query).fetch(batch_size=1000)

    @staticmethod
    def active_dict(is_russian):
        artists = rating_artist.query().filter(rating_artist.is_active == True).filter(rating_artist.is_russian == is_russian)\
            .fetch(projection=[rating_artist.name], batch_size=1000)
        return {a.get_id(): a.name for a in artists}

    @staticmethod
    def active_count():
        return rating_artist.query(rating_artist.is_active==True).count()


class VkRatingStatusManager(object):
    @staticmethod
    def last_state_by_status(service_status):
        result = VkRatingStatus.query()\
            .filter(VkRatingStatus.status == service_status)\
            .order(-VkRatingStatus.date).fetch(1)
        return result[0] if result else None
