# Generated by Django 3.2.8 on 2021-10-28 21:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("landingpages", "0002_landingpage_bots"),
    ]

    operations = [
        migrations.AddField(
            model_name="landingpage",
            name="action_text",
            field=models.CharField(
                blank=True, help_text="The call to action text for this landing page", max_length=128, null=True
            ),
        ),
    ]
