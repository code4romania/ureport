# Generated by Django 3.2.6 on 2021-10-13 12:37

from django.db import migrations

# language=SQL
INDEX_SQL_CONTACTACTIVITY_ORG_DATE_SCHEME_NOT_NULL = """
CREATE INDEX IF NOT EXISTS stats_contactactivity_org_id_date_scheme_not_null on stats_contactactivity (org_id, date, scheme) WHERE scheme IS NOT NULL;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("stats", "0017_better_indexes"),
    ]

    operations = [
        migrations.RunSQL(INDEX_SQL_CONTACTACTIVITY_ORG_DATE_SCHEME_NOT_NULL, ""),
    ]
