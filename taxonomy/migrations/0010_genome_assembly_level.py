# Generated by Django 5.0.1 on 2024-01-15 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0009_remove_taxon_unique_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='genome',
            name='assembly_level',
            field=models.CharField(default='', max_length=200),
        ),
    ]
