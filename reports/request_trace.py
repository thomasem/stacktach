import os
import sys

sys.path.append(os.environ["STACKTACH_INSTALL_DIR"])

from stacktach import models


request_raws = models.RawData.objects.filter(
    request_id="req-8a71e31a-eafe-494b-bfd3-74bad8ad43df"
).values('json')
counter = 1
print os.environ["STACKTACH_DB_HOST"]
for request_raw in request_raws:
    print "----- %s -----" % str(counter)
    print request_raw['json']
    counter = counter+1
