# Generated by Django 3.2.6 on 2021-09-13 12:35

from django.db import migrations

from ureport.sql import InstallSQL


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0067_pollresult_scheme"),
    ]

    operations = [InstallSQL("polls_0068")]
