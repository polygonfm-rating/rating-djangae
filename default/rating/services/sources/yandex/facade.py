import requests
import json
import time
import datetime
import logging
from rating.utils import GzipDecoder, TimeElapsed


class YandexWordstatError(Exception):
    def __init__(self, error_code, error_str, error_detail, ):
        super(YandexWordstatError, self).__init__()
        self.error_code = error_code
        self.error_str = error_str
        self.error_detail = error_detail

    def __str__(self):
        return "Error code: {}. Error: {}. Error detail: {}"\
            .format(self.error_code, self.error_str.encode('utf8'), self.error_detail.encode('utf8'))


class YandexWordstatFacadeError(Exception):
    pass


class YandexWordstatCaptchaError(Exception):
    def __init__(self, captcha_data):
        self.captcha = Captcha(captcha_data)


class Captcha:
    def __init__(self, captcha_data):
        self.url = captcha_data.get('url')
        self.key = captcha_data.get('key')


LOGIN = 'polygonfm-rating'
POINTS_PER_TERM = 10
TOKEN = 'ARa6ZGkAAx3yxSguYhSYQQWVhAE5fd-25g'
UNITS_REST = 'UnitsRest'
DATA = 'data'
ERROR_DETAIL = 'error_detail'
ERROR_STR = 'error_str'
ERROR_CODE = 'error_code'
STATUS_REPORT_DONE = 'Done'
STATUS_REPORT_PENDING = 'Pending'
STATUS_REPORT_FAILED = 'Failed'
REPORT_ID = 'ReportID'
STATUS_REPORT = 'StatusReport'
MAX_REPORTS_COUNT = 5
MAX_PHRASES_IN_REPORT_COUNT = 10


class YandexWordStatFacade:
    YANDEX_WORD_STAT_URL = "https://wordstat.yandex.ru/stat/words"
    WORDS_PARAM = "words"

    def __init__(self):
        self.session = requests.Session()
        self.decoder = GzipDecoder()
        self.is_authenticated = False

    def initialize(self):
        self._delete_old_reports()

    def get_report(self, terms):
        report_id = None
        try:
            report_id = self._create_new_wordstat_report(terms)
        except YandexWordstatError as e:
            # too many reports on the server
            if e.error_code == 31:
                self._delete_old_reports()
                return self.get_report(terms)
            raise

        status = self._wait_report_is_ready(report_id)
        if not status or status == STATUS_REPORT_FAILED:
            return None

        report = self._get_wordstat_report(report_id)
        return dict(self._get_shows_in_month(report))

    def is_enough_units(self, terms):
        units_rest = self._get_client_units()
        return units_rest > POINTS_PER_TERM * len(terms)

    def _get_shows_in_month(self, report):
        for record in report:
            phrase = record['Phrase'].lower()
            for sw in record['SearchedWith']:
                if phrase == sw['Phrase']:
                    yield phrase, sw['Shows']
                    break

    def _wait_report_is_ready(self, report_id):
        def get_report_status():
            reports = self._get_wordstat_report_list()
            return reports[report_id] if report_id in reports else None

        status = STATUS_REPORT_PENDING
        while status == STATUS_REPORT_PENDING:
            time.sleep(5)
            status = get_report_status()
        return status

    def _delete_old_reports(self):
        for report_id in self._get_wordstat_report_list():
            self._delete_wordstat_report(report_id)

    def _create_new_wordstat_report(self, terms):
        return self._call_direct('CreateNewWordstatReport', {'Phrases': terms})

    def _delete_wordstat_report(self, report_id):
        return self._call_direct('DeleteWordstatReport', report_id) == 1

    def _get_wordstat_report(self, report_id):
        return self._call_direct('GetWordstatReport', report_id)

    def _get_wordstat_report_list(self):
        result = self._call_direct('GetWordstatReportList', None)
        return {record[REPORT_ID]: record[STATUS_REPORT] for record in result}

    def _get_client_units(self):
        result = self._call_direct('GetClientsUnits', [LOGIN])
        return result[0][UNITS_REST] if UNITS_REST in result[0] else 0

    def _call_direct(self, method, param):
        params = {'method': method,
                  'token': TOKEN,
                  'param': param,
                  'locale': 'ru'}
        jdata = json.dumps(params, ensure_ascii=False).encode('utf8')
        response = self.session.post("https://api-sandbox.direct.yandex.ru/v4/json/", data=jdata)
        result = json.loads(response.content)
        self._check_for_errors(result)
        return result[DATA]

    def _check_for_errors(self, result):
        if ERROR_CODE in result:
            raise YandexWordstatError(result[ERROR_CODE], result[ERROR_STR], result[ERROR_DETAIL])
