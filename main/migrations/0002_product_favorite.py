# Generated by Django 2.2.5 on 2021-04-22 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='favorite',
            field=models.ManyToManyField(blank=True, to='main.Customer'),
        ),
    ]