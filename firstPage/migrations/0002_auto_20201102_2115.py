# Generated by Django 3.1.2 on 2020-11-02 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstPage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rankings',
            name='rank_date',
            field=models.CharField(max_length=100),
        ),
    ]
