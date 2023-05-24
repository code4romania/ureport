# Generated by Django 3.2.8 on 2021-11-11 14:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0070_install_triggers"),
    ]

    operations = [
        migrations.AddField(
            model_name="pollquestion",
            name="hidden_charts",
            field=models.CharField(
                blank=True,
                choices=[
                    (None, "Show Age, Gender and Location charts"),
                    ("A", "Hide Age chart ONLY"),
                    ("G", "Hide Gender chart ONLY"),
                    ("L", "Hide Location chart ONLY"),
                    ("AG", "Hide Age and Gender charts"),
                    ("AL", "Hide Age and Location charts"),
                    ("GL", "Hide Gender and Location charts"),
                    ("AGL", "Hide Age, Gender and Location charts"),
                ],
                max_length=3,
                null=True,
            ),
        ),
    ]
