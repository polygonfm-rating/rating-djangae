from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from rating.services.views.vk_captcha import VkCaptchaView
from rating.services.views.invalidate_rating import InvalidateRatingView
from rating.views.total_rating import TotalRatingView, TotalRatingViewJSON, TotalRatingViewJSONP
import rating.services.urls
from rating.admin import admin_site

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TotalRatingView.as_view(), name='total_rating'),
    url(r'^json/', TotalRatingViewJSON.as_view()),
    url(r'^jsonp/', TotalRatingViewJSONP.as_view()),
    url(r'^_ah/', include('djangae.urls')),
    url(r'^admin/invalidate_rating$', InvalidateRatingView.as_view(), name='invalidate_rating'),
    url(r'^admin/vk_captcha$', VkCaptchaView.as_view(), name='vk_captcha'),
    url(r'^admin/', include(admin_site.urls)),
    url(r'^jobs/', include(rating.services.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

