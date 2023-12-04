# Generated by Django 4.2.7 on 2023-12-04 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0006_taxon_version_delete_taxonomy_taxon_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accession', models.CharField(unique=True)),
                ('taxon', models.ForeignKey(on_delete=set, to='taxonomy.taxon')),
                ('version', models.ManyToManyField(to='taxonomy.version')),
            ],
        ),
    ]
