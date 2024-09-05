from celery import shared_task
from taxonomy.models import Taxon, Genome, Version
from django.apps import apps
from celery.utils.log import get_task_logger
import os

@shared_task
def taxon_to_list(taxon, version, study, genomelist):
    genomelist_model = apps.get_model(app_label='studies', model_name='GenomeList')
    genomelist_object = genomelist_model.objects.get(id=genomelist)
    taxon = Taxon.objects.get(id=taxon)
    version = Version.objects.get(id=version)
    genomes = []
    taxa_list = []
    taxa_for_genomes = []
    taxa_for_loop = []
    taxa_pre_loop = []
    taxa_for_genomes.append(taxon)
    taxa_for_loop.append(taxon)
    while True:
        if not taxa_for_loop:
            break
        else:
            for parent_tax in taxa_for_loop: 
                taxa_list = Taxon.objects.filter(parent_tax_id=parent_tax.tax_id, version = version)
                for taxon in taxa_list:
                    taxa_for_genomes.append(taxon)
                    taxa_pre_loop.append(taxon)
            taxa_for_loop = taxa_pre_loop
            taxa_pre_loop = []
    for taxon in taxa_for_genomes: 
        genomes_found = Genome.objects.filter(taxon=taxon, version=version).values('id')
        if genomes_found:
            for genome in genomes_found:
                genomes.append(genome['id'])
    genomelist_object.genomes.add(*genomes)
    print (genomelist_object.status)
    genomelist_object.status = 1
    print (genomelist_object.status)
    genomelist_object.save()