# Generated by Django 5.0.1 on 2024-06-27 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0005_remove_traits_genome_genome_trait'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='version_id',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
