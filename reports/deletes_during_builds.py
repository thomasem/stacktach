import report


class DeletesDuringBuildsReport(report.StackTachReport):
    def do_report(self):
        models = self.models
        start_s, end_s = self.start_s, self.end_s
        summary = {'count': 0}
        tenant_breakdown = {}  # {tenant: {uuid: seconds}}}
        report = {'summary': summary, 'report': tenant_breakdown}
        major_events = ['compute.instance.create.start',
                        'compute.instance.delete.start']

        create_uuids = models.RawData.objects.filter(
            when__gt=start_s,
            when__lte=end_s,
            event='compute.instance.create.start'
        ).values('instance').distinct()

        for uuid_dict in create_uuids:
            uuid = uuid_dict['instance']

            # Candidate for super class abstraction.. Like:
            # get_request
            create_request_ids = models.RawData.objects.filter(
                instance=uuid,
                event=major_events[0]
            ).values('request_id').distinct()

            delete_request_ids = models.RawData.objects.filter(
                instance=uuid,
                event=major_events[1]
            ).values('request_id').distinct()

            # Ignore if no delete was ever requested
            if delete_request_ids.count() == 0:
                continue

            tenant = "other"
            create_start = None
            create_end = None
            delete_start = None
            delete_end = None

            # TODO: Make resilient to multiple delete requests

            # Candidate for superclass abstraction
            for request_id_dict in create_request_ids:
                req_id = request_id_dict['request_id']
                raws = models.RawData.objects.filter(
                    request_id=req_id
                ).values('when', 'tenant').order_by('when')
                for raw in raws:
                    if tenant == "other":
                        tenant = raw['tenant']
                    if create_start is None:
                        create_start = raw['when']
                    create_end = raw['when']

            for request_id_dict in delete_request_ids:
                req_id = request_id_dict['request_id']
                raws = models.RawData.objects.filter(
                    request_id=req_id
                ).values('when', 'tenant').order_by('when')
                for raw in raws:
                    if tenant == "other":
                        tenant = raw['tenant']
                    if delete_start is None:
                        delete_start = raw['when']
                    delete_end = raw['when']

            if tenant in ['10009617', '588343', '643895', '620040', '588773',
                          '829659', '10007746', '643798']:
                continue

            delete_after = None
            if delete_start < create_end:
                delete_after = delete_start - create_start
                if delete_after > 0:
                    summary['count'] = summary.get('count', 0) + 1
                    tenant_dict = tenant_breakdown[tenant] = tenant_breakdown.get(
                        tenant, {})
                    current_time = tenant_dict[uuid] = tenant_dict.get(uuid, 0)
                    if current_time == 0 or (current_time > delete_after):
                        tenant_dict[uuid] = delete_after

        return report

    def print_report(self, report_dict):
        summary = report_dict.get('summary', None)
        count = summary.get('count', report_dict.get('count', "No count found"))
        report = report_dict.get('report', None)
        print "%s - Reporting from %s to %s" % (
            self.report_name,
            self.start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            self.end_dt.strftime('%Y-%m-%d %H:%M:%S')
        )
        print "\nTotal deleted during build: %d\n" % count
        if count == 0:
            print "None found for this time period"
        else:
            for tenant, uuids in report.iteritems():
                print "Tenant: %s\n" % tenant
                for uuid, time in uuids.iteritems():
                    formatted_time = self.convert_delta_to_seconds(time)
                    print "\t%s was requested to be deleted %s into the build process" %\
                        (uuid, formatted_time)
                print ""

if __name__ == "__main__":
    name = "Deletes During Builds"
    desc = "StackTach Deletes During Builds"
    report = DeletesDuringBuildsReport(name, desc, 1)
    report_dict = report.do_report()
    if not report.silent:
        report.print_report(report_dict)
    if report.store:
        report.save_report(report_dict)
