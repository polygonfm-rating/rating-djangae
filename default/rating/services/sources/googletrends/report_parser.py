import re
import datetime


def is_trends_chart_data(report):
    return u'google.visualization.Query.setResponse' in report


def parse_chart_data(report):
    result = dict()
    m = re.match("^.*\ngoogle.visualization.Query.setResponse\((.+)\);$", report)
    if m:
        r1 = m.group(1)
        r2 = re.match("^.*\"rows\":\[(.+)\]}}$", r1).group(1)
        # {"c":[{"v":new Date(2016,3,15),"f":"Thursday, April 14, 2016"},{"v":59.0,"f":"59"}]},
        for line in re.findall("({\"c\":\[\{.+?\}\]\})", r2):
            date, interest = __parse_date_interest(line)
            if date and interest:
                result[date] = interest
    return result


def __parse_date_interest(line):
    # {"c":[{"v":new Date(2016,3,15),"f":"Thursday, April 14, 2016"},{"v":59.0,"f":"59"}]},
    m = re.match("^.*new Date\((\d\d\d\d),(\d{1,2}),(\d{1,2})\).+?\"f\":\"(\d+)\"\}\]", line)
    if m:
        date = datetime.date(int(m.group(1)), int(m.group(2)) + 1, int(m.group(3)))
        interest = int(m.group(4))
        return date, interest
    return None, None


def is_trends_report(report):
    return report.startswith(u'Web Search interest:')


def parse(report):
    result = []

    is_report_data = False
    for line in report.split('\n'):
        if is_report_data:
            if line:
                week_interest = __read_week_interest(line)
                if week_interest:
                    result.append(__read_week_interest(line))
            else:
                break

        if not is_report_data and line.startswith(u'Week,'):
            is_report_data = True

    return result


def __read_week_interest(line):
    m = re.match("^(\d\d\d\d)-(\d\d)-(\d\d)\s+-\s+(\d\d\d\d)-(\d\d)-(\d\d),(\d+)", line)
    if m:
        week_from = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        week_to = datetime.date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
        interest = int(m.group(7))
        return week_from, week_to, interest
    return None
