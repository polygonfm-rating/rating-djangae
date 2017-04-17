import datetime
import urllib
from rating import utils
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from rating.services.sources.total import TotalRatingService


class TotalRating:
    def __init__(self, artist_name, rating=0):
        self.artist_name = artist_name
        self.rating = rating


class TotalRatingViewMixin(object):
    def get_rating(self, request):
        date = self.get_date_param(request, 'date')
        return self._get_rating(date)

    def get_date_param(self, request, param):
        for k in request.GET:
            if k.lower() == param:
                try:
                    date = datetime.datetime.strptime(request.GET[k], "%Y-%m-%d").date()
                    return date
                except ValueError:
                    return None
        return None

    def _get_rating(self, for_date=None):
        service = TotalRatingService()
        count = 50
        date = for_date if for_date else utils.today()

        return {'russian_rating': service.get_rating(date, True, count),
                'foreign_rating': service.get_rating(date, False, count),
                'mix_rating': service.get_rating(date, None, 100), }


class TotalRatingView(TemplateView, TotalRatingViewMixin):
    template_name = 'total_rating_view.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        rating = self.get_rating(request)
        for k in rating:
            context[k] = rating[k]
        return self.render_to_response(context)


class JsonpResponse(JsonResponse):
    def __init__(self, callback, data, **kwargs):
        super(JsonpResponse, self).__init__(data=data, **kwargs)
        self['Content-Type'] = 'application/javascript'
        self.content = '{}({});'.format(callback, self.content)


class TotalRatingViewJSON(View, TotalRatingViewMixin):
    def get(self, request, *args, **kwargs):
        return JsonResponse(self.get_rating(request))

CALLBACK = 'callback'


class TotalRatingViewJSONP(View, TotalRatingViewMixin):
    def get(self, request, *args, **kwargs):
        callback = self.__get_callback(request)
        return JsonpResponse(callback, self.get_rating(request)) if callback else JsonResponse(self.get_rating(request))

    def __get_callback(self, request):
        for param in request.GET:
            if param.lower() == CALLBACK:
                return urllib.unquote(request.GET[param]).encode('utf-8')
        return None
