import utils
from django.core.mail import send_mail
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from auth import CustomDatastoreUserManager
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils.html import format_html
from django.db.models.manager import Manager
import urllib
from artists_file import ArtistsReader
from rating.services.sources.googletrends import facade as trends


class ArtistManager(Manager):
    def create_from_file(self, lines, is_russian):
        for artist in ArtistsReader().read(lines, is_russian):
            updated_values = ({'youtube_channel_id': artist.youtube_channel_id,
                               'youtube_user': artist.youtube_user,
                               'is_russian': artist.is_russian,
                               'google_trends_term': artist.google_trends_term,
                               'yandex_wordstat_param': artist.yandex_wordstat,
                               'vk_name': artist.vk_name})
            self.update_or_create(name=artist.name, defaults=updated_values)


YOUTUBE_CHANNEL_URL = "https://www.youtube.com/channel/"
YOUTUBE_USER_URL = "https://www.youtube.com/user/"
LASTFM_UTL = "http://www.last.fm/music/"


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    youtube_channel_id = models.CharField(max_length=200, blank=True)
    youtube_user = models.CharField(max_length=200, blank=True)
    vk_name = models.CharField(max_length=200, blank=True)
    is_russian = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    yandex_wordstat_param = models.CharField(max_length=200, blank=True, null=True)
    google_trends_term = models.CharField(max_length=200, blank=True, null=True)
    objects = ArtistManager()

    def __str__(self):
        return self.name.encode('utf-8') if self.name else self.name

    def quote(self, text):
        return urllib.quote(text.encode('utf-8'), '') if text else ''

    def html_a(self, link, display):
        return format_html("<a href=\"{}\">{}</a>".format(link.encode('utf-8'), display.encode('utf-8'))) \
            if display and link else ''

    def link_youtube(self):
        display, url = (self.youtube_user, YOUTUBE_USER_URL) if self.youtube_user \
            else (self.youtube_channel_id, YOUTUBE_CHANNEL_URL)

        return self.html_a(url + self.quote(display), display)

    def link_lastfm(self):
        return self.html_a(LASTFM_UTL + self.quote(self.name), self.name)

    def link_google_trends(self):
        term = self.google_trends_term if self.google_trends_term else self.name
        quoted = urllib.quote(term.encode('utf-8'), '')
        link = "https://www.google.com/trends/explore#&geo=RU&date=today%201-m&cmpt=q&tz=Etc%2FGMT-3&q={}".format(
            quoted)
        return self.html_a(link, term)

    def link_google_trends_json(self):
        term = self.google_trends_term if self.google_trends_term else self.name
        link = trends.get_report_url(term, utils.month_ago())
        return self.html_a(link, term)

    def link_yandex_wordstat(self):
        term = self.yandex_wordstat_param if self.yandex_wordstat_param else self.name
        quoted = urllib.quote(term.encode('utf-8'), '')
        link = "https://wordstat.yandex.ru/#!/?words={}".format(quoted)
        return self.html_a(link, term)

    def vk_name_column(self):
        return self.vk_name

    link_youtube.short_description = 'YouTube'
    link_lastfm.short_description = 'LastFm'
    link_google_trends.short_description = 'Google Trends'
    link_google_trends_json.short_description = 'Google Trends JSON'
    link_yandex_wordstat.short_description = 'Yandex Wordstat'
    vk_name_column.short_description = 'VKontakte'


class PermissionsMixin(models.Model):
    is_superuser = models.BooleanField(_('superuser status'), default=False,
                                       help_text=_('Designates that this user has all permissions without '
                                                   'explicitly assigning them.'))

    # groups = RelatedSetField(
    #     Group,
    #     verbose_name=_('groups'),
    #     blank=True, help_text=_('The groups this user belongs to. A user will '
    #                             'get all permissions granted to each of '
    #                             'his/her group.')
    # )
    #
    # user_permissions = ListField(
    #     models.CharField(max_length=500),
    #     verbose_name=_('user permissions'), blank=True,
    #     help_text='Specific permissions for this user.'
    # )

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None):
        return True

    def has_perms(self, perm_list, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class CustomDatastoreUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
                                help_text=_('Required. 30 characters or fewer. Letters, digits and '
                                            '@/./+/-/_ only.'),
                                validators=[
                                    validators.RegexValidator(r'^[\w.@+-]+$',
                                                              _('Enter a valid username. '
                                                                'This value may contain only letters, numbers '
                                                                'and @/./+/-/_ characters.'), 'invalid'),
                                ],
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                })
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomDatastoreUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = "rating"
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


        # # def __init__(self):
        # #     self._default_manager = MyDatastoreUserManager()
        # #TODO: add validators
        # username = models.CharField('User Name', max_length=30, unique=True, null=True, default=None)
        # email = models.EmailField('email address', null=True)
        # is_active = models.BooleanField('active', default=True,
        #         help_text='Designates whether this user should be treated as '
        #         'active. Unselect this instead of deleting accounts.')
        #
        # USERNAME_FIELD = 'username'
        # REQUIRED_FIELDS = ['email']
        #
        # objects = MyDatastoreUserManager()
        #
        # class Meta:
        #     app_label = "rating_admin"
        #     swappable = 'AUTH_USER_MODEL'
        #     verbose_name = 'user'
        #     verbose_name_plural = 'users'
        #
        # def get_absolute_url(self):
        #     return "/users/%s/" % urlquote(self.username)
        #
        # def get_full_name(self):
        #     """
        #     Returns the first_name plus the last_name, with a space in between.
        #     """
        #     full_name = '%s %s' % (self.first_name, self.last_name)
        #     return full_name.strip()
        #
        # def get_short_name(self):
        #     "Returns the short name for the user."
        #     return self.first_name
        #
        # def email_user(self, subject, message, from_email=None):
        #     """
        #     Sends an email to this User.
        #     """
        #     send_mail(subject, message, from_email, [self.email])
        #
        # def __str__(self):
        #     """
        #         We have to override this as username is nullable. We either return the email
        #         address, or if there is a username, we return "email (username)".
        #     """
        #     username = self.get_username()
        #     if username:
        #         return "{} ({})".format(six.text_type(self.email), six.text_type(username))
        #     return six.text_type(self.email)
