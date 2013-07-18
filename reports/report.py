import os
import sys
import json
import datetime
import argparse

# Set up Python path
sys.path.append(os.environ.get('STACKTACH_INSTALL_DIR', '/stacktach'))

from stacktach import models
from stacktach import datetime_to_decimal as dt


class TemporalReport(object):
    def __init__(self):
        self.args = self.parser.parse_args()
        self.store = self.args.store
        self.silent = self.args.silent
        time_dict = {
            'days_back': self.args.days_back,
            'hours_back': self.args.hours_back,
            'minutes_back': self.args.minutes_back,
            'days': self.args.days,
            'hours': self.args.hours,
            'minutes': self.args.minutes
        }
        self.start_dt, self.end_dt = self._get_start_end(**time_dict)
        self.start_s, self.end_s = self._convert_start_end_to_seconds(
            self.start_dt,
            self.end_dt
        )

    # Standard storage for JsonReport model
    def store_report(self, report_dict, period_start, period_end, version, name):

        values = {'json': json.dumps(report),
                  'created': dt.dt_to_decimal(datetime.datetime.utcnow()),
                  'period_start': self.start_s,
                  'period_end': self.end_s,
                  'version': self.version,
                  'name': self.report_name}

        report = models.JsonReport(**values)
        report.save()

    def do_report(self):
        # If no report procedure is defined, not implemented.
        raise NotImplementedError()

    def print_report(self, report):
        # If no display defined, not implemented.
        raise NotImplementedError()

    @staticmethod
    def _get_start_end(days_back=0, hours_back=0, minutes_back=0, days=0,
                       hours=0, minutes=0):
        start_report_dt = datetime.datetime.utcnow() - datetime.timedelta(
            days=days_back,
            hours=hours_back,
            minutes=minutes_back
        )
        end_report_dt = start_report_dt + datetime.timedelta(
            days=days,
            hours=hours,
            minutes=minutes
        )
        return (start_report_dt, end_report_dt)

    @staticmethod
    def _convert_start_end_to_seconds(start_dt, end_dt):
        return (dt.dt_to_decimal(start_dt), dt.dt_to_decimal(end_dt))

    @staticmethod
    def convert_delta_to_seconds(delta):
        return dt.sec_to_str(delta)

    @staticmethod
    def _create_default_parser(report_desc):
        parser = argparse.ArgumentParser(report_desc)
        parser.add_argument(
            '--days_back',
            help='Report N days back from now. Default: 0',
            default=0,
            type=int
        )
        parser.add_argument(
            '--hours_back',
            help='Report N hours back from now. Default: 0',
            default=0,
            type=int
        )
        parser.add_argument(
            '--minutes_back',
            help='Report N minutes back from now. Default: 0',
            default=0,
            type=int
        )
        parser.add_argument(
            '--days',
            help='Report span days. Default: 0',
            default=0,
            type=int
        )
        parser.add_argument(
            '--hours',
            help='Report span hours. Default: 0',
            default=0,
            type=int
        )
        parser.add_argument(
            '--minutes',
            help='Report span minutes. Default: 0',
            default=0,
            type=int
        )
        parser.add_argument(
            '--store',
            help="Flag to store report. Default: False",
            default=False,
            type=bool
        )
        parser.add_argument(
            '--silent',
            help="Flag to suppress report print. Default: False",
            default=False,
            type=bool
        )
        return parser
