from djangae.settings_base import * #Set up some AppEngine specific stuff
from django.core.urlresolvers import reverse_lazy
from djangae.contrib.gauth.settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


from .boot import get_app_config
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_app_config().secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# Application definition

INSTALLED_APPS = (
    'djangae', # Djangae needs to come before django apps in django 1.7 and above
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'djangosecure',
#    'csp',
#    'cspreports',
    'djangae.contrib.gauth.datastore',
    'djangae.contrib.security',
    # 'djangae.contrib.uniquetool',
    'rating',
    'rating.services',
)

MIDDLEWARE_CLASSES = (
 #   'djangae.contrib.security.middleware.AppEngineSecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'djangae.contrib.gauth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'csp.middleware.CSPMiddleware',
  #  'session_csrf.CsrfMiddleware',
    'django.middleware.common.CommonMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    #"session_csrf.context_processor"
)

SECURE_CHECKS = [
    "djangosecure.check.sessions.check_session_cookie_secure",
    "djangosecure.check.sessions.check_session_cookie_httponly",
    "djangosecure.check.djangosecure.check_security_middleware",
    "djangosecure.check.djangosecure.check_sts",
    "djangosecure.check.djangosecure.check_frame_deny",
    "djangosecure.check.djangosecure.check_ssl_redirect",
    #"rating_admin.checks.check_session_csrf_enabled",
    #"rating_admin.checks.check_csp_is_not_report_only"
]

# CSP_REPORT_URI = reverse_lazy('report_csp')
# CSP_REPORTS_LOG = True
# CSP_REPORTS_LOG_LEVEL = 'warning'
# CSP_REPORTS_SAVE = True
# CSP_REPORTS_EMAIL_ADMINS = False

AUTH_USER_MODEL = 'rating.CustomDatastoreUser'

AUTHENTICATION_BACKENDS = (
    'rating.auth.CustomAuthenticationBackend',
    #'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'rating.urls'

WSGI_APPLICATION = 'rating.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

ADMIN_EMAIL = "polygonfm.rating@gmail.com"
ADMIN_EMAIL_1 = "olga.kertling@gmail.com"
NO_REPLY_EMAIL = "noreply@polygonfm-rating-dangae.appspotmail.com"

URL_VK_CAPTCHA = "/admin/vk_captcha"
URL_BASE = "https://polygonfm-rating-dangae.appspot.com/"

# if DEBUG:
#     CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
#
# # sensible default CPS settings, feel free to modify them
# CSP_DEFAULT_SRC = ("'self'", "*.gstatic.com")
# CSP_STYLE_SRC = ("'self'", "fonts.googleapis.com", "*.gstatic.com")
# CSP_FONT_SRC = ("'self'", "themes.googleusercontent.com", "*.gstatic.com")
# CSP_FRAME_SRC = ("'self'", "www.google.com", "www.youtube.com", "accounts.google.com", "apis.google.com", "plus.google.com")
# CSP_SCRIPT_SRC = ("'self'", "*.googleanalytics.com", "*.google-analytics.com", "ajax.googleapis.com")
# CSP_IMG_SRC = ("'self'", "data:", "s.ytimg.com", "*.googleusercontent.com", "*.gstatic.com")
# CSP_CONNECT_SRC = ("'self'", "plus.google.com", "www.google-analytics.com")

#CSRF_COOKIE_HTTPONLY = True



