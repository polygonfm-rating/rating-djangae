from google.appengine.ext import ndb


class rating_artist(ndb.Model):
    key = ndb.KeyProperty()
    name = ndb.StringProperty()
    youtube_channel_id = ndb.StringProperty()
    youtube_user = ndb.StringProperty()
    is_russian = ndb.BooleanProperty()
    is_active = ndb.BooleanProperty()
    vk_name = ndb.StringProperty()
    yandex_wordstat_param = ndb.StringProperty()
    google_trends_term = ndb.StringProperty()

    def get_id(self):
        return self._key.id()

    def get_wordstat_term(self):
        return self.yandex_wordstat_param if self.yandex_wordstat_param else self.name


class ServiceStatus(object):
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class RatingStatus(ndb.Model):
    service_name = ndb.StringProperty()
    date = ndb.DateProperty()
    completed_time = ndb.DateTimeProperty()
    status = ndb.StringProperty()


class VkRatingStatus(ndb.Model):
    date = ndb.DateProperty()
    completed_time = ndb.DateTimeProperty()
    status = ndb.StringProperty()
    captcha_required = ndb.BooleanProperty(default=False)
    captcha_for_method = ndb.StringProperty()
    captcha_sid = ndb.StringProperty()
    captcha_img = ndb.StringProperty()
    captcha_value = ndb.StringProperty()


class VkRating(ndb.Model):
    artist_id = ndb.IntegerProperty(indexed=True)
    date = ndb.DateProperty(auto_now_add=True)
    tracks_count = ndb.IntegerProperty(default=0)
    in_popular_count = ndb.IntegerProperty(default=0)
    in_interests_count = ndb.IntegerProperty(default=0)
    rate = ndb.FloatProperty(default=0, indexed=True)


class LastFmRating(ndb.Model):
    artist_id = ndb.IntegerProperty(indexed=True)
    date = ndb.DateProperty()
    plays_count = ndb.IntegerProperty(default=0)
    listeners_count = ndb.IntegerProperty(default=0)
    rate = ndb.FloatProperty(default=0)

    def __repr__(self):
        return '{}: {} {} {}'.format(self.artist_id,
                                     self.plays_count,
                                     self.listeners_count,
                                     self.rate)


class YouTubeRating(ndb.Model):
    artist_id = ndb.IntegerProperty(indexed=True)
    date = ndb.DateProperty()
    view_count = ndb.IntegerProperty(default=0)
    subscriber_count = ndb.IntegerProperty(default=0)
    rate = ndb.FloatProperty(default=0)


class GoogleTrendsRating(ndb.Model):
    artist_id = ndb.IntegerProperty(indexed=True)
    artist_name = ndb.StringProperty()
    collecting_date = ndb.DateProperty()
    date = ndb.DateProperty()
    previous_date = ndb.DateProperty()
    relative_interest_delta = ndb.IntegerProperty(default=0)


class GoogleTrendsRatingStatus(ndb.Model):
    date = ndb.DateProperty()
    completed_time = ndb.DateTimeProperty()
    status = ndb.StringProperty()
    last_valid_date = ndb.DateProperty()


class YandexWordStatRating(ndb.Model):
    artist_id = ndb.IntegerProperty(indexed=True)
    artist_name = ndb.StringProperty()
    collecting_date = ndb.DateProperty()
    date = ndb.DateProperty()
    shows = ndb.IntegerProperty(default=0)


class TotalRating(ndb.Model):
    artist_id = ndb.IntegerProperty(indexed=True)
    is_russian = ndb.BooleanProperty()
    artist_name = ndb.StringProperty()
    date = ndb.DateProperty(indexed=True)
    position = ndb.IntegerProperty(default=0, indexed=True)
    position_mixed = ndb.IntegerProperty(default=0, indexed=True)
    formula_version = ndb.IntegerProperty(default=True)


class TotalRatingFormula(ndb.Model):
    version = ndb.IntegerProperty(default=0)


    # class ArtistsRating(ndb.Model):
    #     artist_id = ndb.StringProperty(indexed=True)
    #     collecting_date = ndb.DateProperty(auto_now_add=True, indexed=True)
    #
    #     vk_tracks_count = ndb.IntegerProperty(default=0)
    #     vk_in_populars_count = ndb.IntegerProperty(default=0)
    #     vk_total_rating = ndb.FloatProperty(default=0)
    #
    #     lastfm_plays_count = ndb.IntegerProperty(default=0)
    #     lastfm_listeners = ndb.IntegerProperty(default=0)
    #     lastfm_total_rating = ndb.FloatProperty(default=0)
    #
    #     total_rating = ndb.FloatProperty(default=0)
