# Generated by Django 3.0.4 on 2020-03-22 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_marks_scored'),
    ]

    operations = [
        migrations.AddField(
            model_name='marks_scored',
            name='total_marks',
            field=models.IntegerField(default=0),
        ),
    ]