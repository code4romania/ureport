import logging
import os

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from dash.orgs.models import Org
from ureport.contacts.models import Contact


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reset the RapidPro Contact import cache in order to do a full import next"

    def handle(self, *args, **options):

        for org in Org.objects.all():
            schemes_populated_key = f"schemes_populated:{org.id}"
            cache.delete(schemes_populated_key)
            logger.info("Reset the schemes import cache for org: %s", org)

            contact_activities_schemes_populated_key = f"contact_activities_schemes_populated:{org.id}"
            cache.delete(contact_activities_schemes_populated_key)

            contact_activities_schemes_max_id_key = f"contact_activities_schemes_max_id:{org.id}"
            cache.delete(contact_activities_schemes_max_id_key)
            logger.info("Reset contact activities schemes import cache for org: %s", org)

            poll_results_schemes_populated_key = f"poll_results_schemes_populated:{org.id}"
            cache.delete(poll_results_schemes_populated_key)
            
            poll_results_schemes_max_id_key = f"poll_results_schemes_max_id:{org.id}"
            cache.delete(poll_results_schemes_max_id_key)
            logger.info("Reset poll results schemes import cache for org: %s", org)

            backends = org.backends.filter(is_active=True)
            for backend_obj in backends:
                last_fetch_date_key = Contact.CONTACT_LAST_FETCHED_CACHE_KEY % (org.pk, backend_obj.slug)
                cache.delete(last_fetch_date_key, None)
            logger.info("Reset the contacts import cache for org: %s", org)



        
