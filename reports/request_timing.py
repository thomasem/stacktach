import os
import sys
import datetime
import argparse
import json

sys.path.append(os.environ.get('STACKTACH_INSTALL_DIR', '/stacktach'))

from stacktach import datetime_to_decimal as dt
from stacktach import models


def report(region=None, threshold=86400, days_back=0, hours_back=0, minutes_back=0, output_file=None):

    end_time = datetime.datetime.utcnow() - datetime.timedelta(days=0)
    start_time = end_time - datetime.timedelta(
        days=days_back,
        hours=hours_back,
        minutes=minutes_back
    )

    end_time_s = dt.dt_to_decimal(end_time)
    start_time_s = dt.dt_to_decimal(start_time)

    regions = []
    deployments = models.Deployment.objects.values('id')

    if region:
        region = region.upper() if region is not None else None
        for deployment in deployments:
            name = deployment.name.upper()
            if region in name.split('.'):
                regions.append(deployment['id'])
    else:
        regions = [deployment['id'] for deployment in deployments]

    # Provide output stream with reporting parameters
    print "\nReporting from %s day(s) %s hour(s) and %s minute(s) back until %s in %s.\n" % (
        days_back,
        hours_back,
        minutes_back,
        end_time.strftime('%Y-%m-%d %h:%m:%s'),
        (region.upper() if region is not None else None)
    )

    updates = models.RawData.objects.filter(
        event="compute.instance.update",
        when__gt=start_time_s,
        when__lt=end_time_s,
        deployment__in=regions
    ).values(
        "request_id"
    ).distinct()

    request_instance_diff_dicts = []

    for req in updates:
        req_id = req['request_id']
        req_raws = models.RawData.objects.filter(
            request_id=req_id
        ).values('when', 'instance').order_by('when')

        start_request_when = None
        end_request_when = None
        instance_id = None

        for raw in req_raws:
            if start_request_when is None:
                start_request_when = raw['when']
            end_request_when = raw['when']
            if instance_id is None and raw['instance'] is not None:
                instance_id = raw['instance']

        if start_request_when and end_request_when:
            diff = end_request_when - start_request_when
            if diff > threshold:
                request_instance_diff_dicts.append({
                    "req_id": req_id,
                    "instance_id": instance_id,
                    "diff_in_seconds": diff
                })

    if len(request_instance_diff_dicts) > 0:
        print "\nTotal requests: %s" % len(updates)
        if output_file:
            with open(output_file, 'w+') as f:
                f.write(json.dumps(
                    ["request: %s, instance: %s, diff: %s seconds" %
                     (req['req_id'], req['instance_id'], req['diff_in_seconds'])
                     for req in request_instance_diff_dicts], indent=4))
        else:
            for request_stats in request_instance_diff_dicts:
                print "\n--------------------------------"
                for k, v in request_stats.iteritems():
                    print "%s: %s" % (k, v)
    else:
        print "No stats found\nNo output file created\n"
        print "Number of requests: %s" % len(updates)
        print "\nConsider broadening the report window to capture more create requests."
    print ""


if __name__ == '__main__':

    parser = argparse.ArgumentParser('StackTach Download Time Percentage of Create Time')
    # Configured arguments
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
        '--region',
        help='Region to report in. Default: None',
        default=None,
        choices=["dfw", "ord", "lon", "syd"],
        type=str
    )
    parser.add_argument(
        "--threshold",
        help="Show a request if it took longer than this. Units: Seconds, Defaults: 86400 (1 day)",
        default=86400,
        type=int
    )
    parser.add_argument(
        '--output_file',
        help='Output file you wish to save dataset to. Default: None',
        default=None,
        type=str
    )

    args = parser.parse_args()

    report(
        region=args.region,
        days_back=args.days_back,
        hours_back=args.hours_back,
        minutes_back=args.minutes_back,
        threshold=args.threshold,
        output_file=args.output_file
    )
