from datetime import datetime
import mail
import requests
import logging
import report_parser
from urllib import urlencode
from requests.structures import CaseInsensitiveDict


class GoogleTrendsFacade(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = self.__default_headers()
        self.is_alive = True

    def __default_headers(self):
        return CaseInsensitiveDict({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Accept-Encoding': ', '.join(('gzip', 'deflate')),
            'Accept': '*/*'
        })

    def get_trends_report(self, term, date_from):
        url = get_report_url(term, date_from)
        response = self.session.get(url)
        report = response.content.decode('utf-8')

        if response.status_code == 200 and report_parser.is_trends_chart_data(report):
            self.is_alive = True
            return report_parser.parse_chart_data(report)
        elif response.status_code != 200:
            self.is_alive = False

        logging.error("GOOGLE TRENDS. Couldn't retrieve report for term {}. URL: {} Response {}"
                      .format(term.encode('utf-8'), url, response.status_code))
        mail.send_no_report(term.encode('utf-8'), url, report, response.status_code)
        return None


def get_date_param(date_from):
    now = datetime.now()
    months_count = (now.year - date_from.year) * 12 - date_from.month + now.month
    return "today {}-m".format(months_count)
    # return "{}/{} {}m".format(date_from.month, date_from.year, months_count)


def get_report_url(term, date_from):
    # http://www.google.com/trends/fetchComponent?hl=en-US&tz=Etc%2FGMT-3&geo=RU&cid=TIMESERIES_GRAPH_0&export=3&q=%2Fm%2F0134s5&date=today+1-m
    data = {"q": term.encode('utf-8'), "cid": "TIMESERIES_GRAPH_0", "export": "3", "hl": "en-US",
            "date": get_date_param(date_from), "geo": "RU", "tz": "Etc/GMT-3"}
    return "http://www.google.com/trends/fetchComponent?" + urlencode(data)
