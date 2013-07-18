import os
import sys
import datetime

sys.path.append(os.environ.get('STACKTACH_INSTALL_DIR', '/stacktach'))

from stacktach import datetime_to_decimal as dt
from stacktach import models

if __name__ == '__main__':

    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(days=1)

    end_time = dt.dt_to_decimal(end_time)
    start_time = dt.dt_to_decimal(start_time)

    hours_threshold = 3
    threshold = 60*(60*hours_threshold)

    # creates = models.Timing.objects.filter(
    #     name='compute.instance.create',
    #     start_when__gt=start_time,
    #     start_when__lt=end_time
    # )
    # # creates_count = creates.count()

    # hung_operations = creates.filter(
    #     end_raw__isnull=True,
    # ).exclude(
    #     lifecycle__last_state="error"
    # )

    # # hung_operations_deleted = hung_operations.filter(
    # #     lifecycle__last_state="deleted"
    # # )

    # hanging_operations = hung_operations.exclude(
    #     lifecycle__last_state='deleted'
    # )

    # hanging_instances = [hanging_operation.lifecycle.instance
    #                      for hanging_operation in hanging_operations]

    # Do we want to use compute.instance.create instead of scheduler
    # notifications? Depends on if we want to look at ones that at least
    # made it to a compute node.

    create_reqs = models.RawData.objects.filter(
        event="scheduler.run_instance.start",
        when__gt=start_time,
        when__lt=end_time
    ).values('request_id').distinct()

    req_ids = [req['request_id'] for req in create_reqs]
    hanging_requests = []
    for req_id in req_ids:
        last_raw = models.RawData.objects.filter(
            request_id=req_id
        ).exclude(
            event='compute.instance.exists'
        ).values(
            "id", "request_id", "when", "routing_key", "old_state",
            "state", "tenant", "event", "image_type", "deployment",
            "instance"
        ).order_by('-when')[0]

        error = False
        if last_raw['state'] == "error":
            error = True
        elif "error" in last_raw['routing_key']:
            error = True
        elif not error and "end" not in last_raw['event']:
            diff = end_time - last_raw['when']
            if diff > threshold:
                hanging_requests.append({
                    'instance_id': last_raw['instance'],
                    'request_id': last_raw['request_id'],
                    'diff': diff,
                    'last_raw': last_raw['id']
                })
    # hanging_request_raws = []
    # for hanging_instance in hanging_instances:
    #     reqs = models.RawData.objects.filter(instance=hanging_instance).values(
    #         "request_id").distinct()

    #     reqs = [req['request_id'] for req in reqs]

    #     for req_id in reqs:
    #         raws = models.RawData.objects.filter(
    #             request_id=req_id
    #         ).order_by(
    #             "when"
    #         )
    #         raw_before = raws[0]
    #         for raw in raws[1:]:
    #             diff = raw.when - raw_before.when
    #             if diff > threshold:
    #                 hanging_request_raws.append({
    #                     'raw': raw_before,
    #                     'diff': diff
    #                 })
    #             if (raw is raws[len(raws)-1]) and (raw.event != "compute.instance.create.end"):
    #                 diff = end_time - raw.when
    #                 if diff > threshold:
    #                     hanging_request_raws.append({
    #                         'raw': raw,
    #                         'diff': diff
    #                     })
    #             raw_before = raw

    # hanging_operations_count = 0
    # for operation in hanging_operations:
    #     uuid = operation.lifecycle.instance
    #     if (end_time - operation.start_when) > threshold:
    #         print "Instance: %s" % uuid
    #         reqs = models.RawData.objects.filter(instance=uuid).values('request_id').distinct()
    #         for req in reqs:
    #             print"\tRequest: %s" % str(req['request_id'])
    #         hanging_operations_count = hanging_operations_count + 1

    # hung_operations_count = 0
    # for operation in hung_operations_deleted:
    #     lifecycle = operation.lifecycle
    #     instance = lifecycle.instance
    #     delete_start = models.RawData.objects.filter(
    #         instance=instance,
    #         event='compute.instance.delete.start'
    #     )[0]

    #     if (delete_start.when - start_time) > threshold:
    #         hung_operations_count = hung_operations_count + 1
    # percent_hung = (float(hanging_operations_count) /
    #                 creates_count)*100
    # print "Total creates: %s" % str(creates_count)
    # print "Currently hanging operations: %s" % str(hanging_operations_count)
    # print "Deleted hung operations: %s" % str(hung_operations_count)
    # print "Percent hung: %.2f" % (percent_hung)
    print "Hanging request count: %s" % str(len(hanging_requests))
    for hanging_request in hanging_requests:
        print "------------------------------------"
        print "Instance: %s" % str(hanging_request['instance_id'])
        print "Request: %s" % str(hanging_request['request_id'])
        print "Diff: %s" % str(datetime.timedelta(seconds=int(hanging_request['diff'])))
        print "Last Raw ID: %s" % str(hanging_request['last_raw'])
