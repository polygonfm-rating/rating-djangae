from rating.services.datastore import TotalRatingFormula as RatingFormula


class TotalRatingFormula(object):

    def __init__(self):
        self._version = None

    def _get_version(self):
        if not self._version:
            result = RatingFormula.query().fetch(1)
            self._version = result[0] if result else RatingFormula()
        return self._version

    @property
    def version(self):
        return self._get_version().version

    def increase_version(self):
        version = self._get_version()
        version.version += 1
        version.put()