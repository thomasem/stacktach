import os
import sys
import datetime

sys.path.append(os.environ.get('STACKTACH_INSTALL_DIR', '/stacktach'))

from stacktach import datetime_to_decimal as dt
from stacktach import models

if __name__ == '__main__':

    hours_threshold = 3
    threshold = 60*(60*hours_threshold)

    end_time = datetime.datetime.utcnow() - datetime.timedelta(
        hours=hours_threshold
    )
    start_time = end_time - datetime.timedelta(days=1)

    end_time = dt.dt_to_decimal(end_time)
    start_time = dt.dt_to_decimal(start_time)

    create_requests = models.RawData.objects.filter(
        event="scheduler.run_instance.start",
        when__gt=start_time,
        when__lt=end_time
    ).values(
        "request_id"
    ).distinct()

    not_scheduled = []
    scheduled_not_started = []

    for req in create_requests:
        req_id = req['request_id']
        req_raws = models.RawData.objects.filter(
            request_id=req_id
        )

        scheduled = False
        compute_started = False
        error = False
        for raw in req_raws:
            if not error and raw.state == "error":
                error = True
                break
            if raw.event == "scheduler.run_instance.scheduled":
                instance_id = raw.instance
                scheduled = True
            elif raw.event == "compute.instance.create.start":
                compute_started = True

        if scheduled and not compute_started and not error:
            scheduled_not_started.append({
                'request_id': req_raws[0].request_id,
                'instance_id': instance_id if instance_id is not None else "None"
            })

    print "Scheduled but not started count: %s" % str(len(scheduled_not_started))
    for req_id in scheduled_not_started:
        print "Request ID: %s" % str(req_id)
