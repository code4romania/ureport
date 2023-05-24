# Generated by Django 4.1.7 on 2023-04-06 13:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stats", "0026_populate_flow_result_word_clouds"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactActivityCounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("is_squashed", models.BooleanField(default=False)),
                ("date", models.DateField(help_text="The starting date for for the month")),
                (
                    "type",
                    models.CharField(
                        choices=[("A", "All"), ("B", "Age"), ("G", "Gender"), ("L", "Location"), ("S", "Scheme")],
                        help_text="The type of alert the counter segment",
                        max_length=1,
                    ),
                ),
                ("value", models.CharField(max_length=255)),
                ("count", models.IntegerField(default=0, help_text="Number of items with this counter")),
                ("org", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="orgs.org")),
            ],
        ),
        migrations.AddIndex(
            model_name="contactactivitycounter",
            index=models.Index(
                fields=["org", "date", "type", "value", "count"], name="contact_activitycntr_org_count"
            ),
        ),
    ]
