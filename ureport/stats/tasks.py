import logging
import time
from datetime import timedelta

from django.utils import timezone

from dash.orgs.models import Org
from dash.orgs.tasks import org_task
from ureport.celery import app
from ureport.utils import chunk_list

logger = logging.getLogger(__name__)


@org_task("refresh-engagement-data", 60 * 60 * 4)
def refresh_engagement_data(org, since, until):
    from .models import PollStats

    start = time.time()

    time_filters = list(PollStats.DATA_TIME_FILTERS.keys())
    segments = list(PollStats.DATA_SEGMENTS.keys())
    metrics = list(PollStats.DATA_METRICS.keys())

    for time_filter in time_filters:
        for segment in segments:
            for metric in metrics:
                PollStats.refresh_engagement_data(org, metric, segment, time_filter)
                logger.info(
                    f"Task: refresh_engagement_data org {org.id} in progress for {time.time() - start}s, for time_filter - {time_filter}, segment - {segment}, metric - {metric}"
                )

    PollStats.calculate_average_response_rate(org)

    logger.info(f"Task: refresh_engagement_data org {org.id} finished in {time.time() - start}s")


@org_task("delete-old-contact-activities", 60 * 60 * 1)
def delete_old_contact_activities(org, since, until):
    from .models import ContactActivity

    now = timezone.now()
    start_time = time.time()
    last_used_time = now - timedelta(days=400)

    # find objects older than 400 days that have used=True so we can update them to used = False
    old_contact_activities_ids = (
        ContactActivity.objects.filter(org=org, date__lte=last_used_time).order_by("id").values_list("id", flat=True)
    )

    org_count = 0

    for batch in chunk_list(old_contact_activities_ids, 1000):
        batch_ids = list(batch)
        deleted, old_objects_deleted = ContactActivity.objects.filter(id__in=batch_ids).delete()

        org_count += deleted

        elapsed = time.time() - start_time

        logger.info(f"Task: Deleting {org_count} old contact activities on org #{org.id} in {elapsed:.1f} seconds")

    elapsed = time.time() - start_time
    logger.info(
        f"Task: Finished deleting {org_count} old contact activities until {last_used_time} on org #{org.id} in {elapsed:.1f} seconds"
    )


@app.task(name="stats.squash_contact_activities_counts")
def squash_contact_activities_counts():
    from .models import ContactActivityCounter

    ContactActivityCounter.squash()


@app.task(name="stats.rebuild_contacts_activities_counts")
def rebuild_contacts_activities_counts():
    from .models import ContactActivity, PollStats

    time_filters = list(PollStats.DATA_TIME_FILTERS.keys())
    segments = list(PollStats.DATA_SEGMENTS.keys())
    metric = "active-users"

    orgs = Org.objects.filter(is_active=True)
    for org in orgs:
        start_rebuild = time.time()

        ContactActivity.recalculate_contact_activity_counts(org)
        logger.info(
            f"Task: rebuild_contacts_activities_counts finished recalculating contact activity counts for org {org.id} in {time.time() - start_rebuild}s"
        )

        start_refresh = time.time()

        for time_filter in time_filters:
            for segment in segments:
                PollStats.refresh_engagement_data(org, metric, segment, time_filter)
                logger.info(
                    f"Task: rebuild_contacts_activities_counts refreshing contacts activities engagement stats for org {org.id} in progress for {time.time() - start_refresh}s, for time_filter - {time_filter}, segment - {segment}, metric - {metric}"
                )
        logger.info(
            f"Task: rebuild_contacts_activities_counts finished recalculating contact activity and refreshing contacts activities engagement stats for org {org.id} in {time.time() - start_rebuild}s"
        )
