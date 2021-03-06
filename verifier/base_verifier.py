# Copyright (c) 2012 - Rackspace Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import datetime
import os
import sys
import time
import multiprocessing

from django.db import transaction


POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'stacktach')):
    sys.path.insert(0, POSSIBLE_TOPDIR)

from stacktach import stacklog, message_service
LOG = stacklog.get_logger('verifier')


def _has_field(d1, d2, field1, field2=None):
    if not field2:
        field2 = field1

    return d1.get(field1) is not None and d2.get(field2) is not None


def _verify_simple_field(d1, d2, field1, field2=None):
    if not field2:
        field2 = field1

    if not _has_field(d1, d2, field1, field2):
        return False
    else:
        if d1[field1] != d2[field2]:
            return False

    return True


def _verify_date_field(d1, d2, same_second=False):
    if d1 and d2:
        if d1 == d2:
            return True
        elif same_second and int(d1) == int(d2):
            return True
    return False


class Verifier(object):
    def __init__(self, config, pool=None, reconciler=None):
        self.config = config
        self.pool = pool or multiprocessing.Pool(config.pool_size())
        self.enable_notifications = config.enable_notifications()
        self.reconciler = reconciler
        self.results = []
        self.failed = []

    def clean_results(self):
        pending = []
        finished = 0
        successful = 0

        for result in self.results:
            if result.ready():
                finished += 1
                if result.successful():
                    (verified, exists) = result.get()
                    if self.reconciler and not verified:
                        self.failed.append(exists)
                    successful += 1
            else:
                pending.append(result)

        self.results = pending
        errored = finished - successful
        return len(self.results), successful, errored

    def _keep_running(self):
        return True

    def _utcnow(self):
        return datetime.datetime.utcnow()

    def _run(self, callback=None):
        tick_time = self.config.tick_time()
        settle_units = self.config.settle_units()
        settle_time = self.config.settle_time()
        while self._keep_running():
            with transaction.commit_on_success():
                now = self._utcnow()
                kwargs = {settle_units: settle_time}
                ending_max = now - datetime.timedelta(**kwargs)
                new = self.verify_for_range(ending_max, callback=callback)
                values = ((self.exchange(), new,) + self.clean_results())
                if self.reconciler:
                    self.reconcile_failed()
                msg = "%s: N: %s, P: %s, S: %s, E: %s" % values
                LOG.info(msg)
            time.sleep(tick_time)

    def run(self):
        if self.enable_notifications:
            exchange_name = self.exchange()
            exchange = message_service.create_exchange(
                exchange_name, 'topic',
                durable=self.config.durable_queue())
            routing_keys = self.config.topics()[exchange_name]

            with message_service.create_connection(
                self.config.host(), self.config.port(),
                self.config.userid(), self.config.password(),
                "librabbitmq", self.config.virtual_host()) as conn:
                def callback(result):
                    (verified, exist) = result
                    if verified:
                        self.send_verified_notification(
                            exist, conn, exchange, routing_keys=routing_keys)

                try:
                    self._run(callback=callback)
                except Exception, e:
                    print e
                    raise e
        else:
            self._run()

    def verify_for_range(self, ending_max, callback=None):
        pass

    def reconcile_failed(self):
        pass

    def exchange(self):
        pass
