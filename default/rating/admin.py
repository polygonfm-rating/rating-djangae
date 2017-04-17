from django.contrib import admin
from django.conf.urls import url
from functools import update_wrapper
from models import *
from django.contrib.admin import AdminSite
from views.artist.upload import UploadArtistsView
from views.artist.download import DownloadArtistsView


class RatingAdminSite(AdminSite):
    site_header = 'PolygonFM Rating Administration'


admin_site = RatingAdminSite()


@admin.register(CustomDatastoreUser, site=admin_site)
class AdminCustomDatastoreUser(admin.ModelAdmin):
    pass


@admin.register(Artist, site=admin_site)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'vk_name_column', 'link_youtube', 'link_lastfm', 'link_google_trends',
                    'link_google_trends_json', 'link_yandex_wordstat',
                    'is_russian', 'is_active')
    list_filter = ('is_russian', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('link_youtube', 'link_lastfm', 'link_google_trends',
                       'link_google_trends_json', 'link_yandex_wordstat',)
    ordering = ('name', 'is_active',)

    fieldsets = (
        (None, {
            'fields': ('name', 'is_russian', 'is_active'),
        }),
        ('Search Parameters', {
            'fields': ('vk_name', 'youtube_channel_id', 'youtube_user', 'google_trends_term', 'yandex_wordstat_param'),
        }),
        ('Links', {
            'fields': ('link_youtube', 'link_lastfm', 'link_google_trends',
                       'link_google_trends_json', 'link_yandex_wordstat'),
        }),
    )

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        base_urls = super(ArtistAdmin, self).get_urls()
        new_urls = [url(r'^upload/$', wrap(UploadArtistsView.as_view()), name="upload"),
                    url(r'^download/rus$', wrap(DownloadArtistsView.as_view()), name="download_rus"),
                    url(r'^download/frg$', wrap(DownloadArtistsView.as_view()), name="download_frg"), ]
        return new_urls + base_urls
