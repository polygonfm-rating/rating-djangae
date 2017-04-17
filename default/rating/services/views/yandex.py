# from django.shortcuts import render_to_response
# from django.template import RequestContext
# from django.views.generic import TemplateView
# from rating.models import Artist
# from rating.services.datastore import YandexWordstatProcessing
# from rating.services.sources.yandex.facade import YandexWordStatFacade, YandexWordstatCaptchaError
#
#
# class YandexProcessingView(TemplateView):
#     template_name = 'services/yandex/rating_view.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(YandexProcessingView, self).get_context_data(**kwargs)
#         context['completed_rating_process'] = self._get_completed_ratings()
#         return context
#
#     def post(self, request, *args, **kwargs):
#
#         context = self.get_context_data(**kwargs)
#         context['captcha_required'] = False
#
#         if 'start_process_hidden_id' in request.POST:
#             artists = Artist.objects.all().filter(is_active=True)
#             service = YandexWordStatFacade()
#             for a in artists:
#                 param = a.yandex_wordstat_param if a.yandex_wordstat_param else a.name
#                 try:
#                     r = service.get_word_stat(param)
#                 except YandexWordstatCaptchaError as e:
#                     context['captcha_required'] = True
#                     context['captcha_url'] = e.captcha.url
#                     context['captcha_key'] = e.captcha.key
#                     break
#
#         elif 'captcha_text_id' in request.POST and 'captcha_key_hidden_id' in request.POST:
#             captcha_text = request.POST['captcha_text_id']
#             captcha_key = request.POST['captcha_key_hidden_id']
#
#             artists = Artist.objects.all().filter(is_active=True)
#             service = YandexWordStatFacade()
#             for a in artists:
#                 param = a.yandex_wordstat_param if a.yandex_wordstat_param else a.name
#                 try:
#                     r = service.get_word_stat(param, captcha_key, captcha_text)
#                 except YandexWordstatCaptchaError as e:
#                     context['captcha_required'] = True
#                     context['captcha_url'] = e.captcha.url
#                     context['captcha_key'] = e.captcha.key
#                     break
#
#         # TODO continue
#         return render_to_response(self.template_name, context=context,
#                                   context_instance=RequestContext(request))
#
#     def _get_completed_ratings(self):
#         return (CompletedRating(p.date, format('{}.{}', p.month_of_rating, p.year_of_rating), p.status)
#                 for p in YandexWordstatProcessing.query().order(YandexWordstatProcessing.date))
#
#
# class CompletedRating:
#     def __init__(self, date, period, status):
#         self.date = date
#         self.period = period
#         self.status = status
