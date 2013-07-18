import os
import sys
import datetime
import math
import argparse
import json

sys.path.append(os.environ.get('STACKTACH_INSTALL_DIR', '/stacktach'))

from stacktach import datetime_to_decimal as dt
from stacktach import models


def report(region, days_back=0, hours_back=0, minutes_back=0, output_file=None):

    # Terminal evaluations for RawData entry (which task is downloading?)
    def start_block_device_mapping(raw):
        return (raw.old_task == "networking" and raw.task == "block_device_mapping")

    def stop_block_device_mapping(raw):
        return (raw.old_task == "block_device_mapping" and raw.task == "spawning")

    def start_instance_build(raw):
        return (raw.event == "compute.instance.create.start")

    def start_networking(raw):
        return (raw.old_task != "networking" and raw.task == "networking")

    end_time = datetime.datetime.utcnow() - datetime.timedelta(days=0)
    start_time = end_time - datetime.timedelta(
        days=days_back,
        hours=hours_back,
        minutes=minutes_back)

    end_time = dt.dt_to_decimal(end_time)
    start_time = dt.dt_to_decimal(start_time)

    region = region.upper()
    regions = []
    deployments = models.Deployment.objects.all()
    for deployment in deployments:
        name = deployment.name.upper()
        if region == str(name.split('.')[0]):
            regions.append(deployment.id)

    # Provide output stream with reporting parameters
    print "\nReporting from %s day(s) %s hour(s) and %s minute(s) back until %s in %s.\n" % (
        days_back,
        hours_back,
        minutes_back,
        datetime.datetime.utcnow(),
        region.upper()
    )

    create_requests = models.RawData.objects.filter(
        event="compute.instance.create.start",
        when__gt=start_time,
        when__lt=end_time,
        deployment__in=regions
    ).values(
        "request_id"
    ).distinct()

    # To aggregate percentages
    download_percentage_of_creates = []

    # To map instance/request IDs to percentage
    instance_request_percentage_map = []

    for req in create_requests:
        req_id = req['request_id']
        req_raws = models.RawData.objects.filter(
            request_id=req_id
        ).order_by('when')

        instance_id = list(req_raws)[-1].instance if len(req_raws) > 0 else None

        start_request_when = None
        end_request_when = None
        start_timing = None
        end_timing = None


        for raw in req_raws:
            if start_request_when is None:
                start_request_when = raw.when
            if start_block_device_mapping(raw):
                start_timing = raw.when
            elif stop_block_device_mapping(raw):
                end_timing = raw.when
            end_request_when = raw.when

        if start_request_when and end_request_when and start_timing and end_timing:
            diff = end_request_when - start_request_when
            download_time = end_timing - start_timing
            perc = (download_time/diff) * 100
            download_percentage_of_creates.append(perc)
            instance_request_percentage_map.append({
                "uuid": instance_id,
                "req_id": req_id,
                "download_percentage_of_create": perc
            })

    # Operations to get average and standard deviation
    average = 0
    if len(download_percentage_of_creates) > 0:
        # Get average
        for percentage in download_percentage_of_creates:
            average += percentage
        average = average / len(download_percentage_of_creates)

        # Get variance
        variance = 0
        for percentage in download_percentage_of_creates:
            variance += math.pow(percentage - average, 2)
        variance = variance / (len(download_percentage_of_creates) - 1)

        # Standard deviation
        standard_deviation = math.sqrt(variance)

    if len(download_percentage_of_creates) > 0:
        print "Sample size: %s" % len(download_percentage_of_creates)
        print "\nAverage percent of create time for download: %.2f%%" % average
        print "Standard deviation: %.2f" % standard_deviation
        print "\nTotal create requests: %s" % len(create_requests)
        if output_file:
            with open(output_file, 'w+') as f:
                f.write(json.dumps(
                    ["instance: %s, request: %s, download_percentage_of_create: %.2f%%" %
                     (perc['uuid'], perc['req_id'], perc['download_percentage_of_create'])
                     for perc in instance_request_percentage_map],
                    indent=4))
    else:
        print "No stats found\nNo output file created\n"
        print "Number of create requests: %s" % len(create_requests)
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
        help='Region to report in. Defaults: DFW',
        default="dfw",
        choices=["dfw", "ord"],
        type=str
    )
    parser.add_argument(
        '--output_file',
        help='Output file you wish to save dataset to. Default: None',
        default=None,
        type=str
    )

    args = parser.parse_args()

    report(region=args.region,
           days_back=args.days_back,
           hours_back=args.hours_back,
           minutes_back=args.minutes_back,
           output_file=args.output_file
           )
