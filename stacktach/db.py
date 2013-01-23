import models

def create_lifecycle(**kwargs):
    return models.Lifecycle(**kwargs)

def find_lifecycles(**kwargs):
    return models.Lifecycle.objects.select_related().filter(**kwargs)

def create_timing(**kwargs):
    return models.Timing(**kwargs)

def find_timings(**kwargs):
    return models.Timing.objects.select_related().filter(**kwargs)

def save(obj):
    obj.save()