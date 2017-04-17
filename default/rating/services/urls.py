from django.conf.urls import url
from rating.services.views import jobs

urlpatterns = [
    url(r'^vk/$', jobs.run_vk),
    url(r'^lastfm/$', jobs.run_lastfm),
    url(r'^youtube/$', jobs.run_youtube),
    url(r'^googletrends/$', jobs.run_google_trends),
    url(r'^yandex/$', jobs.run_yandex_wordstat),

    url(r'^total/$', jobs.run_total_rating),
    url(r'^check/$', jobs.run_check_rating_completed),
]
